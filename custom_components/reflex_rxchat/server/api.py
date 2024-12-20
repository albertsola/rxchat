from fastapi import WebSocket, APIRouter
from reflex_rxchat.server.chat_server import ChatServer
from typing import List
import uuid
from reflex_rxchat.server.events import Message

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
async def get_conversation_id(conversation_id: str) -> dict:
    return chat_server.conversations[conversation_id].tail(10).dict()


@router.get("/conversations", response_model=List[dict])
async def get_conversations():
    response = []
    conversations = chat_server.get_coverstations()
    for conversation in conversations.values():
        response.append(
            {"id": conversation.id, "users_count": conversation.user_count()}
        )
    return response


@router.post("/conversation/{conversation_id}/join")
async def join_conversation(username: str, conversation_id: str):
    await chat_server.user_join(username, conversation_id)


@router.post("/conversation/{conversation_id}/leave")
async def leave_conversation(username: str, conversation_id: str):
    await chat_server.user_leave(username, conversation_id)


@router.put("/conversation/{conversation_id}/message")
async def message(username: str, conversation_id: str, content: str):
    message = Message(
        username=username,
        conversation_id=conversation_id,
        content=content
    )
    await chat_server.send_message(message)
