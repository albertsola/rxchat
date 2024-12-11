from typing import AsyncGenerator
from aiohttp import ClientSession, WSServerHandshakeError
from rxchat.chat_events import ClientMessage, ServerMessage, Message, LeaveConversation, JoinConversation


class ChatClient:
    def __init__(self, base_url: str):
        self.base_url: str = base_url
        self._session = ClientSession(base_url=base_url)

    async def connect(self, username: str):
        try:
            self.ws = await self._session.ws_connect("/chat", params={"username": username})
        except WSServerHandshakeError as e:
            await self._session.close()
            raise e

    async def receive(self) -> AsyncGenerator[ServerMessage, None]:
        while True:
            data: dict = await self.ws.receive_json()
            yield Message(*data)

    async def send(self, message: ClientMessage):
        await self.ws.send_str(message.json())

    async def join_conversation(self, conversation_id: str):
        await self.send(JoinConversation(conversation_id=conversation_id))

    async def leave_conversation(self, conversation_id: str):
        await self.send(LeaveConversation(conversation_id=conversation_id))

    async def message(self, conversation_id:str, content: str):
        await self.send(Message(conversation_id=conversation_id, content=content))
