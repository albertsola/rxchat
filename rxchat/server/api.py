from fastapi import WebSocket, APIRouter
from rxchat.server.chat_server import ChatServer
from typing import List
import uuid
from .events import Conversation
chat_server = ChatServer()
router = APIRouter()


@router.websocket("/chat")
async def connect_chat(websocket: WebSocket):
    username: str = websocket.query_params.get("username", str(uuid.uuid4()))
    try:
        await chat_server.handle_user_websocket(username, websocket)
    finally:
        await chat_server.handle_user_disconnected(username)

@router.get("/chat/{conversation_id}")
async def get_conversation_id(conversation_id: str) -> Conversation:
    return chat_server.conversations[conversation_id].tail(10)

@router.get("/channels", response_model=List[str])
async def get_channels():
    return ["Welcome", "Jokes", "Tech"]
