import asyncio
from . import logger
from .interfaces import ChatServerInterface, WebSocketClientHandlerInterface
from .models import Conversation

from fastapi.websockets import WebSocket
from reflex_rxchat.server.events import (
    Message,
    ServerMessage,
    EventUserLeaveConversation,
    EventUserJoinConversation,
    ResponseJoinConversation,
)
from typing import Optional

from .websocket_handler import WebSocketClientHandler

default_conversations: dict[str, Conversation] = {
    "Welcome": Conversation(id="Welcome", title="Welcome"),
    "Tech": Conversation(id="Tech", title="Tech"),
    "Jokes": Conversation(id="Jokes", title="Jokes"),
}


class ChatServer(ChatServerInterface):
    def __init__(self) -> None:
        self.conversations: dict[str, Conversation] = default_conversations
        self.users: dict[str, WebSocketClientHandlerInterface] = {}

    def get_users(self) -> dict[str, WebSocketClientHandlerInterface]:
        return self.users

    def get_conversations(self) -> dict[str, Conversation]:
        return self.conversations

    async def handle_user_websocket(self, username: str, ws: WebSocket) -> None:
        handler: WebSocketClientHandlerInterface = WebSocketClientHandler(ws, username)
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
        await self.notify(
            username,
            ResponseJoinConversation(
                conversation_id=conversation_id, users=conversation.usernames
            ),
        )
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
        await self.send_message(
            EventUserLeaveConversation(
                conversation_id=conversation_id, username=username
            )
        )
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
            logger.warning(
                f"Unable to notify {username} message={message} as it is not in users"
            )
            return
        await self.users[username].send(message)

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
