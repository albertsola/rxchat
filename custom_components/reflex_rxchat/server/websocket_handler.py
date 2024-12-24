import asyncio
from typing import AsyncGenerator
from . import logger
from .interfaces import WebSocketClientHandlerInterface, ChatServerInterface
from .events import (
    EventType,
    ServerMessage,
    Message,
    RequestJoinConversation,
    RequestLeaveConversation,
)

from starlette.websockets import WebSocket, WebSocketState, WebSocketDisconnect


class WebSocketClientHandler(WebSocketClientHandlerInterface):
    def __init__(self, ws: WebSocket, username: str):
        self.ws: WebSocket = ws
        self.username: str = username

    def is_connected(self) -> bool:
        return self.ws.state == WebSocketState.CONNECTED

    async def __call__(self, chat_state: ChatServerInterface) -> None:
        try:
            await self.ws.accept()
            logger.info(f" - {self.username} connected")
            async for message in self.receive():
                if message.event == EventType.CONVERSATION_MESSAGE:
                    message.username = self.username
                    try:
                        await chat_state.send_message(message)
                    finally:
                        pass
                elif message.event == EventType.REQUEST_CONVERSATION_JOIN:
                    await chat_state.user_join(self.username, message.conversation_id)
                elif message.event == EventType.REQUEST_CONVERSATION_LEAVE:
                    await chat_state.user_leave(self.username, message.conversation_id)
                else:
                    raise RuntimeError(f"Unknown message type {message.event}")
        except (
            WebSocketDisconnect,
            asyncio.CancelledError,
            StopAsyncIteration,
            StopAsyncIteration,
        ):
            pass
        finally:
            logger.info(f" - {self.username} disconnected")
            users = chat_state.get_users()
            if self.username in users.keys():
                del users[self.username]
            await self.close()

    async def receive(self) -> AsyncGenerator[ServerMessage, None]:  # type: ignore
        try:
            while True:
                data = await self.ws.receive_json()
                if not isinstance(data, dict):
                    raise RuntimeError(
                        f"Server received malformed message. payload={data}"
                    )

                match (data.get("event", None)):
                    case EventType.CONVERSATION_MESSAGE:
                        yield Message(**data)
                    case EventType.REQUEST_CONVERSATION_JOIN:
                        yield RequestJoinConversation(**data)
                    case EventType.REQUEST_CONVERSATION_LEAVE:
                        yield RequestLeaveConversation(**data)
                    case _:
                        raise RuntimeError(
                            f"Server received unknown message. payload={data}"
                        )
        except StopAsyncIteration:
            logger.info(f"WebSocket for {self.username} stream ended gracefully.")
            pass

    async def send(self, message: ServerMessage) -> None:
        await self.ws.send_text(message.json())

    async def close(self):
        if self.is_connected():
            await self.ws.close()
