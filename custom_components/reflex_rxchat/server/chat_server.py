import asyncio
from . import logger
from fastapi.websockets import WebSocket, WebSocketState
from reflex_rxchat.server.events import (
    Message,
    Conversation,
    RequestJoinConversation,
    RequestLeaveConversation,
    ServerMessage,
    ClientMessage,
    EventUserLeaveConversation,
    EventUserJoinConversation,
    ResponseJoinConversation
)
from typing import AsyncGenerator, Optional
from starlette.websockets import WebSocketDisconnect


class WebSocketClientHandler:
    def __init__(self, ws: WebSocket, username: str):
        self.ws: WebSocket = ws
        self.username: str = username

    def is_connected(self):
        self.ws.state == WebSocketState.CONNECTED

    async def __call__(self, chat_state: "ChatServer") -> None:
        try:
            await self.ws.accept()
            logger.info(f" - {self.username} connected")
            async for message in self.receive():
                if message.event == "conversation.message":
                    message.username = self.username
                    try:
                        await chat_state.send_message(message)
                    finally:
                        pass
                elif message.event == "request.conversation.join":
                    await chat_state.user_join(self.username, message.conversation_id)
                elif message.event == "request.conversation.leave":
                    await chat_state.user_leave(self.username, message.conversation_id)
                else:
                    raise RuntimeError(f"Unknown message type {message.event}")
        except StopAsyncIteration:
            pass
        except WebSocketDisconnect as ex:
            pass
        except (asyncio.CancelledError, StopAsyncIteration):
            pass
        finally:
            logger.info(f" - {self.username} disconnected")
            if self.username in chat_state.users:
                del chat_state.users[self.username]
            await self.close()

    async def receive(self) -> AsyncGenerator[ServerMessage, None]:

        while True:
            data = await self.ws.receive_json()
            match (data.get("event", None)):
                case "conversation.message":
                    yield Message(**data)
                case "request.conversation.join":
                    yield RequestJoinConversation(**data)
                case "request.conversation.leave":
                    yield RequestLeaveConversation(**data)
                case _:
                    raise RuntimeError(
                        f"Server received unknown message. payload={data}"
                    )

    async def send(self, message: ServerMessage) -> None:
        await self.ws.send_text(message.json())

    async def close(self):
        if self.is_connected():
            await self.ws.close()


default_conversations: dict[str, Conversation] = {
    "Welcome": Conversation(id="Welcome", title="Welcome"),
    "Tech": Conversation(id="Tech", title="Tech"),
    "Jokes": Conversation(id="Jokes", title="Jokes"),
}


class ChatServer:
    def __init__(self) -> None:
        self.conversations: dict[str, Conversation] = default_conversations
        self.users: dict[str, WebSocketClientHandler] = {}
        self.tasks: list[asyncio.Task] = []

    async def handle_user_websocket(self, username: str, ws: WebSocket) -> None:
        handler: WebSocketClientHandler = WebSocketClientHandler(ws, username)
        self.users[username] = handler
        await handler(self)

    async def handle_user_disconnected(self, username: str) -> None:
        for cid, c in self.conversations.items():
            if username not in c.usernames:
                continue
            c.usernames.remove(username)
            await self.send_message(
                Message(
                    conversation_id=cid,
                    username="_system",
                    content=f"User {username} disconnected.",
                )
            )

    async def user_join(self, username: str, conversation_id: str) -> None:
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = Conversation(
                id=conversation_id, title="Unknown"
            )
        conversation: Conversation = self.conversations[conversation_id]
        if username in conversation.usernames:
            return
        conversation.usernames.append(username)
        await self.notify(username, ResponseJoinConversation(
            conversation_id=conversation_id,
            users=conversation.usernames
        ))
        await self.send_message(
            EventUserJoinConversation(
                conversation_id=conversation_id,
                username=username,
            )
        )

    async def user_leave(self, username: str, conversation_id: str) -> None:
        if conversation_id not in self.conversations:
            # raise RuntimeError("Username is not in the conversation")
            return
        conversation: Conversation = self.conversations[conversation_id]
        if username not in conversation.usernames:
            return
        await self.send_message(EventUserLeaveConversation(
            conversation_id=conversation_id,
            username=username
        ))
        conversation.usernames.remove(username)

    async def send_message(self, message: ServerMessage) -> None:
        if message.conversation_id not in self.conversations.keys():
            raise RuntimeError(f"Conversation {message.conversation_id=} not found")
        conversation: Conversation = self.conversations[message.conversation_id]
        conversation.add_message(message)
        tasks: list[asyncio.Task] = [
            asyncio.create_task(self.notify(username, message))
            for username in conversation.usernames
        ]
        await asyncio.gather(*tasks)

    async def notify(self, username: str, message: ServerMessage) -> None:
        if username not in self.users:
            logger.warning(f"Unable to notify {username} message={message} as it is not in users")
            return
        await self.users[username].send(message)

    def get_converstations(self) -> dict[str, Conversation]:
        return self.conversations

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        if conversation_id not in self.conversations:
            return None
        return self.conversations[conversation_id]

    async def close(self, notify=False, content="Server is shutting down", timeout=2):

        if notify:
            logger.info("Notifying server stopping...")
            message = Message(
                username="_system", conversation_id="_system", content=content
            )
            tasks = [
                asyncio.create_task(user_handler.send(message))
                for user_handler in self.users.values()
            ]
            await asyncio.gather(*tasks)
            await asyncio.sleep(timeout)

        t = []
        for user_handler in self.users.values():
            t.append(asyncio.create_task(user_handler.close()))
        await asyncio.gather(*t)
