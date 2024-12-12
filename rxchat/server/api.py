from fastapi import WebSocket, APIRouter
from rxchat.server.chat_server import ChatServer
import uuid

chat_server = ChatServer()
router = APIRouter()


@router.websocket("/chat")
async def connect_chat(websocket: WebSocket):
    username: str = websocket.query_params.get("username", str(uuid.uuid4()))
    try:
        await chat_server.handle_user_websocket(username, websocket)
    finally:
        await chat_server.handle_user_disconnected(username)
