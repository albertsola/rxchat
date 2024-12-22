from typing import Optional, Dict, AsyncGenerator
from abc import ABC, abstractmethod
from .events import ServerMessage
from .models import Conversation
from fastapi import WebSocket


class WebSocketClientHandlerInterface(ABC):

    def is_connected(self) -> bool:
        pass

    async def __call__(self, chat_state: "ChatServerInterface") -> None:
        pass

    async def receive(self) -> AsyncGenerator[ServerMessage, None]:
        pass

    async def send(self, message: ServerMessage) -> None:
        pass

    async def close(self):
        pass


class ChatServerInterface(ABC):
    conversations: Dict[str, Conversation]
    users: Dict[str, WebSocketClientHandlerInterface]

    def get_users(self) -> Dict[str, WebSocketClientHandlerInterface]:
        """Retrieve the current users connected to the server."""
        pass

    def get_conversations(self) -> Dict[str, Conversation]:
        """Retrieve all conversations on the server."""
        pass

    async def handle_user_websocket(self, username: str, ws: WebSocket) -> None:
        """Handle a user's WebSocket connection."""
        pass

    async def handle_user_disconnected(self, username: str) -> None:
        """Handle disconnection of a user."""
        pass

    async def user_join(self, username: str, conversation_id: str) -> None:
        """Add a user to a conversation."""
        pass

    async def user_leave(self, username: str, conversation_id: str) -> None:
        """Remove a user from a conversation."""
        pass

    async def send_message(self, message: ServerMessage) -> None:
        """Send a message to all users in a conversation."""
        pass

    async def notify(self, username: str, message: ServerMessage) -> None:
        """Send a notification to a specific user."""
        pass

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Retrieve a specific conversation by its ID."""
        pass

    async def close(self, notify: bool = False, content: str = "Server is shutting down", timeout: int = 2) -> None:
        """Close the server and optionally notify users."""
        pass
