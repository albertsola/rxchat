import asyncio
from fastapi import WebSocket
from rxchat.events import Message, Conversation, JoinConversation, ServerMessage, ClientMessage
from typing import AsyncGenerator


class WebSocketClientHandler:
    def __init__(self, ws: WebSocket, username: str):
        self.ws: WebSocket = ws
        self.username: str = username

    async def __call__(self, chat_state: "ChatServer") -> None:
        try:
            await self.ws.accept()
            async for message in self.receive():
                if message.event == "conversation.message":
                    message.username = self.username
                    try:
                        await chat_state.send_message(message)
                    finally:
                        pass
                elif message.event == "conversation.join":
                    await chat_state.user_join(self.username, message.conversation_id)
                elif message.event == "conversation.leave":
                    await chat_state.user_leave(self.username, message.conversation_id)
                else:
                    raise RuntimeError(f"Unknown message type {message.event}")
        except (asyncio.CancelledError, StopAsyncIteration):
            await self.ws.close()

    async def receive(self) -> AsyncGenerator[ServerMessage, None]:
        try:
            while True:
                data = await self.ws.receive_json()
                match (data.get("event", None)):
                    case "conversation.message":
                        yield Message(**data)
                    case "conversation.join":
                        yield JoinConversation(**data)
                    case _:
                        raise RuntimeError(
                            f"Server received unknown message. payload={data}"
                        )
        except StopAsyncIteration:
            pass

    async def send(self, message: ClientMessage) -> None:
        await self.ws.send_text(message.json())


class ChatServer:
    def __init__(self) -> None:
        self.conversations: dict[str, Conversation] = {}
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
            self.conversations[conversation_id] = Conversation()
        conversation: Conversation = self.conversations[conversation_id]
        if username in conversation.usernames:
            return
        conversation.usernames.append(username)
        await self.send_message(
            Message(
                conversation_id=conversation_id,
                username="_system",
                content=f"{username} joined the conversation.",
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
            Message(
                conversation_id=conversation_id,
                username="_system",
                content=f"{username} left the conversation.",
            )
        )
        conversation.usernames.remove(username)

    async def send_message(self, message: Message) -> None:
        if message.conversation_id not in self.conversations.keys():
            raise RuntimeError(f"Conversation {message.conversation_id=} not found")
        conversation: Conversation = self.conversations[message.conversation_id]
        conversation.add_message(message)
        tasks: list[asyncio.Task] = [
            asyncio.create_task(self.notify(username, message))
            for username in conversation.usernames
        ]
        await asyncio.gather(*tasks)

    async def notify(self, username: str, message: Message) -> None:
        if username not in self.users:
            return
        await self.users[username].send(message)
