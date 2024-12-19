from typing import Optional, AsyncGenerator
from ..server import ServerMessage
from ..client import ChatClient, ChatClientInterface
from pydantic import BaseModel
import reflex as rx


class SerializableChatClient(rx.Model, ChatClientInterface):
    base_url: str = ""
    username: str = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.base_url = base_url
        # self.username = username
        self.chat = ChatClient(self.base_url)
        self.chat.connect(self.username)

    async def connect(self, username):
        await self.chat.connect(username)

    async def receive(self) -> AsyncGenerator[ServerMessage, None]:
        async for message in self.chat.receive():
            yield message

    async def send(self, message):
        await self.chat.send(message)

    async def join_conversation(self, conversation_id):
        await self.chat.join_conversation(conversation_id)

    async def leave_conversation(self, conversation_id):
        await self.leave_conversation(conversation_id)

    async def message(self, conversation_id, content):
        await self.message(conversation_id, content)

    async def disconnect(self):
        await self.disconnect()









