# type: ignore
import pytest
from unittest.mock import AsyncMock
from reflex_rxchat.server.events import Message

from .ws_client import WebSocketChatClient


@pytest.fixture
def client():
    WebSocketChatClient.__init__ = lambda _, base_url: None
    client = WebSocketChatClient(base_url="xyz")
    client._session = AsyncMock()
    client.ws = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_connect_success(client: WebSocketChatClient):
    await client.connect(username="testuser")
    client._session.ws_connect.assert_awaited_once()


@pytest.mark.asyncio
async def test_receive_message(client: WebSocketChatClient):
    client.ws.receive_json = AsyncMock(
        side_effect=[
            {"conversation_id": "conv1", "username": "test", "content": "Hello", "event": "conversation.message"},
            {"conversation_id": "conv2", "username": "test", "content": "World", "event": "conversation.message"},
        ]
    )

    received = []
    try:
        async for m in client.receive():
            received.append(m)
    except (StopAsyncIteration, RuntimeError):
        pass
    assert len(received) == 2


@pytest.mark.asyncio
async def test_send_message(client: WebSocketChatClient):
    await client.connect(username="testuser")
    message = Message(conversation_id="x", username="test", content="y")

    # Directly sending the constructed message
    await client.send(message)
    client.ws.send_str.assert_awaited_once_with(message.json())


@pytest.mark.asyncio
async def test_join_conversation(client: WebSocketChatClient):

    await client.connect(username="testuser")
    await client.join_conversation("test_conv")
    client.ws.send_str.assert_awaited_once()


@pytest.mark.asyncio
async def test_leave_conversation(client: WebSocketChatClient):

    await client.connect(username="testuser")
    await client.leave_conversation("test_conv")
    client.ws.send_str.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_plain_message(client: WebSocketChatClient):

    await client.connect(username="testuser")
    await client.message("test_conv", "Hi!")
    client.ws.send_str.assert_awaited_once()
