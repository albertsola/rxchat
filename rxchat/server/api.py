from fastapi import WebSocket, APIRouter
from rxchat.server.chat_server import ChatServer
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

@router.get("/conversation/{conversation_id}")
async def get_conversation_id(conversation_id: str) -> Conversation:
    return chat_server.conversations[conversation_id].tail(10)

@router.get("/conversations", response_model=List[dict])
async def get_conversations():
    response = []
    default_conversations: List[str] = ["Welcome", "Jokes", "Tech"]
    
    for conversation_id in default_conversations:
        conversation = chat_server.get_conversation(conversation_id)
        if not conversation:
            converstation_users_count = 0
        else:
            converstation_users_count = conversation.user_count()

        response.append({
            "id": conversation_id,
            "users_count": converstation_users_count
        })
    return response

