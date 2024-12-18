from fastapi import WebSocket, APIRouter
from rxchat.server.chat_server import ChatServer
from rxchat.server.chat_channel import ChatChannel, get_channel_ids
from typing import Dict, List
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

@router.get("/channels", response_model=List[ChatChannel])
async def get_channels():
    response = []
    for channel_id in get_channel_ids():
        channel_conversation = chat_server.get_conversation(channel_id)
        if not channel_conversation:
            channel_users_count = 0
        else:
            channel_users_count = channel_conversation.user_count()

        response.append({
            "id": channel_id,
            "users_count": channel_users_count
        })
    return response

