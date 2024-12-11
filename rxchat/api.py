import asyncio
import reflex as rx
from fastapi import WebSocket, routing
from rxchat.models import Message, Conversation, ServerMessage, ClientMessage


class WebSocketClientHandler:
    def __init__(self, ws: WebSocket, username: str):
        self.ws: WebSocket = ws
        self.username: str = username

    async def __invoke__(self, chat_state: "ChatServerState"):
        try:
            await self.ws.accept()
            while True:
                message = self.receive()
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
        except asyncio.CancelledError:
            self.ws.close()

    async def receive(self) -> ServerMessage:
        data = await self.ws.receive_json()
        return Message(**data)

    async def send(self, message: ClientMessage):
        await self.ws.send_text(message.json())


class ChatServerState:
    def __init__(self):
        self.conversations: dict[str, Conversation] = {}
        self.users: dict[str, WebSocketClientHandler] = {}
        self.tasks: list[asyncio.Task] = []

    async def handle_user_websocket(self, username: str, ws: WebSocket):
        handler: WebSocketClientHandler = WebSocketClientHandler(ws, username)
        self.users[username] = handler
        await handler()

    async def handle_user_disconnected(self, username: str):
        for cid, c in self.conversations.items():  # type: Conversation
            if username not in c.usernames:
                continue
            c.usernames.remove(username)
            await self.send_message(cid, "_system", f"User {username} disconnected.")

    async def user_join(self, username: str, conversation_id: str):
        if not conversation_id in self.conversations:
            self.conversations[conversation_id] = Conversation()
        conversation: Conversation = self.conversations[conversation_id]
        if username in conversation.usernames:
            return
        conversation.usernames.append(username)
        await self.send_message(conversation_id, "_system", f"{username} joined the conversation.")

    async def user_leave(self, username: str, conversation_id: str):
        if not conversation_id in self.conversations:
            return
        conversation: Conversation = self.conversations[conversation_id]
        if username in conversation.usernames:
            return
        await self.send_message(conversation_id, "_system", f"{username} left the conversation.")
        conversation.usernames.remove(username)

    async def send_message(self, message: Message):
        if message.conversation_id not in self.conversations.keys():
            raise RuntimeError(f"Conversation {message.conversation_id=} not found")
        conversation: Conversation = self.conversations[message.conversation_id]
        conversation.add_message(message)
        tasks: list[asyncio.Task] = [asyncio.create_task(self.notify(username, message)) for username in
                                     conversation.usernames]
        await asyncio.gather(*tasks)

    async def notify(self, username: str, message: Message):
        if username not in self.users:
            return
        await self.users[username].send(message)


chat_server = ChatServerState()


@routing.WebSocket("/chat/{username}")
async def connect_chat(username: str, websocket: WebSocket):
    try:
        await chat_server.handle_user_websocket(username, websocket)
    finally:
        await chat_server.handle_user_disconnected(username)
