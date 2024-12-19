import reflex as rx
import aiohttp

from reflex_rxchat.client import ChatClient
from reflex_rxchat.server import Message


class ChatState(rx.State):
    """The app state."""

    _chat: ChatClient | None = None
    connected: bool = False
    conversations_data: dict[str, dict] = {}
    conversations: list[str] = ["Welcome"]

    messages: list[Message] = []
    conversation_id: str = "Welcome"
    conversation_user_count: int = 0
    content: str = ""
    username: str = ""
    processing: bool = False

    @rx.var(cache=True)
    def backend_url(self) -> str:
        frontend_scheme: str = self.router.page.host.split(":")[0]
        backend_hostname: str = self.router.headers.host
        return f"{frontend_scheme}://{backend_hostname}/"

    @rx.event(background=True)
    async def connect(self):
        try:
            async with self:
                if self.username.__len__() < 5:
                    yield rx.toast.error(
                        "Your username has to be at least 5 characters long"
                    )
                    return
            backend_url = self.backend_url
            async with self:
                print("Initializing chat client")
                chat = ChatClient(base_url=backend_url)
                self._chat = chat
                await chat.connect(self.username)
                await chat.join_conversation(self.conversation_id)
                self.connected = True
            async for m in chat.receive():
                async with self:
                    self.messages.append(m)
        except Exception as ex:
            print(f"Exception chat client {ex}")
            async with self:
                yield rx.toast.error(f"Error: {ex}")
            raise ex

        finally:
            print("Chat client finalizing")
            async with self:
                self.connected = False
                self.messages = []

    @rx.event
    async def change_conversation(self, conversation_id: str):
        assert (
            self._chat is not None
        ), "ChatState._chat needs to be initialized to change_conversation"
        await self.leave_conversation(self.conversation_id)
        self.conversation_id = conversation_id
        await self.join_conversation(self.conversation_id)

    @rx.event
    async def join_conversation(self, conversation_id: str):
        assert self._chat is not None
        await self._chat.join_conversation(conversation_id)
        await self.update_conversations(self.conversation_id)

    @rx.event
    async def leave_conversation(self, conversation_id: str):
        assert self._chat is not None
        await self._chat.leave_conversation(conversation_id)

    @rx.event
    async def send_message(self, form_data: dict):
        assert (
            self._chat is not None
        ), "ChatState._chat needs to be initialized to send a message"
        self.processing = True
        self.content = form_data["content"]
        if not self.content:
            return
        await self._chat.send_message(self.conversation_id, self.content)
        self.content = ""
        self.processing = False

    @rx.event
    async def disconnect(self):
        await self._chat.disconnect()

    @staticmethod
    async def fetch_conversations():
        """Fetch the list of conversations from the backend."""
        url = "http://localhost:8000/conversations"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        print(
                            f"Failed to fetch conversations. Status code: {response.status}"
                        )
                        return []
        except Exception as e:
            print(f"Error fetching conversations: {e}")
            return []

    @rx.event
    async def load_conversations(self):
        """Load the conversations into the state."""
        conversations = await self.fetch_conversations()

        if conversations:
            self.conversations_data = {
                conversation["id"]: conversation for conversation in conversations
            }
            self.conversations = [
                f"{conversation['id']}" for conversation in conversations
            ]

    async def update_conversations(self, conversation_id):
        await self.load_conversations()
        self.conversation_user_count = self.conversations_data[conversation_id][
            "users_count"
        ]
