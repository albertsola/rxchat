import reflex as rx
import aiohttp

from rxchat.client import ChatClient
from rxchat.server import Message
from rxchat.server.chat_channel import ChatChannel

class ChatState(rx.State):
    """The app state."""

    _chat: ChatClient | None = None
    connected: bool = False
    channels_data: dict[str, ChatChannel] = {}
    channels: list[str] = ["Welcome"]

    messages: list[Message] = []
    conversation_id: str = "Welcome"
    conversation_user_count: int = 0
    content: str = ""
    username: str = ""
    processing: bool = False

    def backend_url(self) -> str:
        frontend_scheme: str = self.router.page.host.split(":")[0]
        backend_hostname: str = self.router.headers.host
        return f"{frontend_scheme}://{backend_hostname}/"
        
    @rx.event(background=True)
    async def connect(self):
        try:
            async with self:
                if self.username.__len__() < 5:
                    return rx.toast.error("Your username has to be at least 5 characters long")
            backend_url = self.backend_url()
            async with self:
                self._chat = ChatClient(base_url=backend_url)
                await self._chat.connect(self.username)
                await self.join_conversation(self.conversation_id)
                self.connected = True
            async for m in self._chat.receive():
                async with self:
                    self.messages.append(m)
        except Exception as ex:
            async with self:
                return rx.toast.error(f"Error: {ex}")

        finally:
            async with self:
                self._chat = None
                self.connected = False
                self.messages = []

    @rx.event
    async def change_conversation(self, conversation_id: str):
        assert self._chat is not None, "ChatState._chat needs to be initialized to change_conversation"
        await self.leave_conversation(self.conversation_id)
        self.conversation_id = conversation_id
        await self.join_conversation(self.conversation_id)

    @rx.event
    async def join_conversation(self, conversation_id: str):
        assert self._chat is not None
        await self._chat.join_conversation(conversation_id)
        await self.update_channel(self.conversation_id)

    @rx.event
    async def leave_conversation(self, conversation_id: str):
        assert self._chat is not None
        await self._chat.leave_conversation(conversation_id)

    @rx.event
    async def send_message(self, form_data: dict):
        assert self._chat is not None, "ChatState._chat needs to be initialized to send a message"
        self.processing = True
        self.content = form_data['content']
        if not self.content:
            return
        await self._chat.send_message(self.conversation_id, self.content)
        self.content = ""
        self.processing = False

    @rx.event
    async def disconnect(self):
        await self._chat.disconnect()

    @staticmethod
    async def fetch_channels():
        """Fetch the list of channels from the backend."""
        url = f"http://localhost:8000/channels"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        print(f"Failed to fetch channels. Status code: {response.status}")
                        return []
        except Exception as e:
            print(f"Error fetching channels: {e}")
            return []
    
    @rx.event
    async def load_channels(self):
        """Load the channels into the state."""
        channels = await self.fetch_channels()
        
        if channels:
            self.channels_data = {channel['id']: channel for channel in channels}
            self.channels = [f"{channel['id']}" for channel in channels]

    async def update_channel(self, conversation_id):
        await self.load_channels()
        self.conversation_user_count = self.channels_data[conversation_id]["users_count"]