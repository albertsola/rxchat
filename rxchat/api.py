from fastapi import WebSocket, APIRouter
from rxchat.chat_server import ChatServer
from uuid import UUID

chat_server = ChatServer()
router = APIRouter()


@router.websocket("/chat")
async def connect_chat(websocket: WebSocket):
    username: str = websocket.query_params.get("username", str(UUID()))
    try:
        await chat_server.handle_user_websocket(username, websocket)
    finally:
        await chat_server.handle_user_disconnected(username)
