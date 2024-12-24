from typing import AsyncGenerator, Optional
from aiohttp import (
    ClientSession,
    WSServerHandshakeError,
    ClientWebSocketResponse,
    WSMessageTypeError,
)
from reflex_rxchat.server import (
    ClientMessage,
    Message,
    RequestLeaveConversation,
    RequestJoinConversation,
)
from reflex_rxchat.server.events import (
    EventType,
    ServerMessage,
    EventUserJoinConversation,
    EventUserLeaveConversation,
    ResponseJoinConversation,
)


class WebSocketChatClient:
    def __init__(self, base_url: str) -> None:
        self.base_url: str = base_url
        self._session: ClientSession = ClientSession(base_url=base_url)
        self.ws: Optional[ClientWebSocketResponse] = None
        self.username: Optional[str] = None

    async def connect(self, username: str):
        try:
            self.ws = await self._session.ws_connect(
                "/chat", params={"username": username}
            )
            self.username = username
        except WSServerHandshakeError as e:
            await self._session.close()
            raise e

    async def receive(self) -> AsyncGenerator[ServerMessage, None]:
        while True:
            assert (
                self.ws is not None
            ), "ChatClient.ws can't be None when calling receive()"
            try:
                data: dict = await self.ws.receive_json()
            except WSMessageTypeError:
                return

            match (data.get("event", None)):
                case EventType.CONVERSATION_MESSAGE:
                    yield Message(**data)

                case EventType.RESPONSE_CONVERSATION_JOIN:
                    yield ResponseJoinConversation(**data)

                case EventType.EVENT_CONVERSATION_JOIN:
                    yield EventUserJoinConversation(**data)
                case EventType.EVENT_CONVERSATION_LEAVE:
                    yield EventUserLeaveConversation(**data)
                case _:
                    raise RuntimeError(
                        f"Server received unknown message. payload={data}"
                    )

    async def send_message(self, conversation_id: str, content: str):
        await self.send(
            Message(
                conversation_id=conversation_id, content=content, username=self.username
            )
        )

    async def send(self, message: ClientMessage):
        assert self.ws is not None, "ChatClient.ws can't be None when calling send()"
        await self.ws.send_str(message.json())

    async def join_conversation(self, conversation_id: str):
        await self.send(RequestJoinConversation(conversation_id=conversation_id))

    async def leave_conversation(self, conversation_id: str):
        await self.send(RequestLeaveConversation(conversation_id=conversation_id))

    async def message(self, conversation_id: str, content: str):
        await self.send(
            Message(
                conversation_id=conversation_id, username=self.username, content=content
            )
        )

    async def disconnect(self):
        if not self.ws.closed:
            await self.ws.close()
        if not self._session.closed:
            await self._session.close()
