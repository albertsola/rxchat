import asyncio

import reflex as rx

from reflex_rxchat.client import WebSocketChatClient
from reflex_rxchat.server import ServerMessage

from reflex_rxchat.client import ChatRestClient

CHAT_ENDPOINT:str = "http://localhost:8000"
chat: ChatRestClient = ChatRestClient(CHAT_ENDPOINT)


class ChatState(rx.State):
    """The app state."""

    connected: bool = False
    conversations_data: dict[str, dict] = {}
    conversations: list[str] = ["Welcome"]

    messages: list[ServerMessage] = []
    conversation_id: str = "Welcome"
    content: str = ""
    username: str = ""
    conversation_users: list[str] = []
    processing: bool = False

    @rx.var(cache=True)
    def conversation_user_count(self) -> int:
        return len(self.conversation_users)

    @rx.event(background=True)
    async def connect(self):

        try:
            async with self:
                if self.username.__len__() < 5:
                    yield rx.toast.error(
                        "Your username has to be at least 5 characters long"
                    )
                    return
            ws_chat: WebSocketChatClient = WebSocketChatClient(base_url=CHAT_ENDPOINT)
            await ws_chat.connect(self.username)
            await ws_chat.join_conversation(self.conversation_id)
            async with self:
                self.connected = True
            async for m in ws_chat.receive():
                print(m)
                async with self:
                    self.messages.append(m)
                    if m.event == "conversation.message":
                        yield rx.toast(m.content)
                    elif m.event == "response.conversation.join":
                        self.conversation_users = m.users
                        self.conversation_id = m.conversation_id
                    elif m.event == "event.conversation.join":
                        if m.username not in self.conversation_users:
                            self.conversation_users.append(m.username)
                    elif m.event == "event.conversation.leave":
                        self.conversation_users.remove(m.username)
                    else:
                        pass
        except Exception as ex:
            print(f"Exception chat client {ex}")
            async with self:
                yield rx.toast.error(f"Error: {ex}")
            raise ex

        finally:
            await asyncio.sleep(3)
            print("Chat client finalizing")
            async with self:
                self.connected = False
                self.messages = []
            if ws_chat is not None:
                await ws_chat.disconnect()

    @rx.event
    async def change_conversation(self, conversation_id: str):
        await chat.leave_conversation(self.username, self.conversation_id)
        self.conversation_id = conversation_id
        await chat.join_conversation(self.username, self.conversation_id)

    @rx.event
    async def join_conversation(self, conversation_id: str):
        await chat.join_conversation(self.username, conversation_id)
        await self.update_conversations(self.conversation_id)

    @rx.event
    async def leave_conversation(self, conversation_id: str):
        await chat.leave_conversation(self.username, conversation_id)
        await self.update_conversations(self.conversation_id)

    @rx.event
    async def send_message(self, form_data: dict):
        self.processing = True
        self.content = form_data["content"]
        if not self.content:
            return
        await chat.send_message(self.username, self.conversation_id, self.content)
        self.content = ""
        self.processing = False

    @rx.event
    async def disconnect(self):
        return rx.toast("Disconnect is Not implemented")

    @rx.event
    async def load_conversations(self):
        """Load the conversations into the state."""
        conversations = await chat.get_conversations()

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
