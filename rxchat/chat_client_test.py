import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from unittest import mock
from aiohttp import WSServerHandshakeError
from .chat_events import Message, JoinConversation, LeaveConversation

from .chat_client import ChatClient  # adjust the import to match your project structure


@pytest.fixture
def client():
    ChatClient.__init__ = lambda _, base_url: None
    client = ChatClient(base_url="xyz")
    client._session = AsyncMock()
    client.ws = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_connect_success(client: ChatClient):
    await client.connect(username="testuser")
    client._session.ws_connect.assert_awaited_once()


@pytest.mark.asyncio
async def test_receive_message(client: ChatClient):
    mock_ws = AsyncMock()
    client.ws.receive_json = AsyncMock(side_effect=[
        {"conversation_id": "conv1", "username": "test", "content": "Hello"},
        {"conversation_id": "conv2", "username": "test", "content": "World"},
    ])

    received = []
    try:
        async for m in client.receive():
            received.append(m)
    except (StopAsyncIteration, RuntimeError):
        pass
    assert len(received) == 2


@pytest.mark.asyncio
async def test_send_message(client: ChatClient):
    await client.connect(username="testuser")
    message = Message(
        conversation_id="x",
        username="test",
        content="y"
    )

    # Directly sending the constructed message
    await client.send(message)
    client.ws.send_str.assert_awaited_once_with(message.json())


@pytest.mark.asyncio
async def test_join_conversation(client: ChatClient):

    await client.connect(username="testuser")
    await client.join_conversation("test_conv")
    client.ws.send_str.assert_awaited_once()


@pytest.mark.asyncio
async def test_leave_conversation(client: ChatClient):

    await client.connect(username="testuser")
    await client.leave_conversation("test_conv")
    client.ws.send_str.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_plain_message(client: ChatClient):

    await client.connect(username="testuser")
    await client.message("test_conv", "Hi!")
    client.ws.send_str.assert_awaited_once()
