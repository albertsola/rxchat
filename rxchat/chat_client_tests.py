import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from aiohttp import WSServerHandshakeError
from .chat_events import Message, JoinConversation, LeaveConversation

from .chat_client import ChatClient  # adjust the import to match your project structure


@pytest.mark.asyncio
async def test_connect_success():
    # Mock the ws_connect method to return a mock websocket
    mock_ws = MagicMock()
    mock_session = AsyncMock()
    mock_session.ws_connect.return_value = mock_ws

    with patch('aiohttp.ClientSession', return_value=mock_session):
        client = ChatClient(base_url="http://testserver")
        await client.connect(username="testuser")

        mock_session.ws_connect.assert_awaited_once_with("/chat", params={"username": "testuser"})
        assert client.ws == mock_ws


@pytest.mark.asyncio
async def test_connect_failure():
    mock_session = AsyncMock()
    mock_session.ws_connect.side_effect = WSServerHandshakeError(message='fail', request_info=None, history=())

    with patch('aiohttp.ClientSession', return_value=mock_session):
        client = ChatClient(base_url="http://testserver")

        with pytest.raises(WSServerHandshakeError):
            await client.connect(username="testuser")

        # Ensure session was closed after exception
        mock_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_receive_message():
    # Setup a mock websocket that yields JSON data
    mock_ws = AsyncMock()
    mock_ws.receive_json = AsyncMock(side_effect=[
        {"conversation_id": "conv1", "content": "Hello"},
        {"conversation_id": "conv2", "content": "World"},
        asyncio.CancelledError  # Stop iteration
    ])

    mock_session = AsyncMock(ws_connect=AsyncMock(return_value=mock_ws))
    with patch('aiohttp.ClientSession', return_value=mock_session):
        client = ChatClient(base_url="http://testserver")
        await client.connect(username="testuser")

        received_messages = []
        async for msg in client.receive():
            received_messages.append(msg)
            if len(received_messages) == 2:
                break

        assert len(received_messages) == 2
        assert received_messages[0].conversation_id == "conv1"
        assert received_messages[0].content == "Hello"
        assert received_messages[1].conversation_id == "conv2"
        assert received_messages[1].content == "World"


@pytest.mark.asyncio
async def test_send_message():
    mock_ws = AsyncMock()
    mock_ws.send_str = AsyncMock()

    mock_session = AsyncMock(ws_connect=AsyncMock(return_value=mock_ws))

    # We'll mock the Message class's json method
    with patch('rxchat.chat_events.ClientMessage') as MockClientMessage:
        mock_message_instance = MagicMock()
        mock_message_instance.json.return_value = '{"conversation_id":"conv1","content":"Hello"}'
        MockClientMessage.return_value = mock_message_instance

        with patch('aiohttp.ClientSession', return_value=mock_session):
            client = ChatClient(base_url="http://testserver")
            await client.connect(username="testuser")

            # Directly sending the constructed message
            await client.send(mock_message_instance)
            mock_ws.send_str.assert_awaited_once_with('{"conversation_id":"conv1","content":"Hello"}')


@pytest.mark.asyncio
async def test_join_conversation():
    mock_ws = AsyncMock()
    mock_ws.send_str = AsyncMock()

    mock_session = AsyncMock(ws_connect=AsyncMock(return_value=mock_ws))

    # Mock JoinConversation
    with patch('rxchat.chat_events.JoinConversation') as MockJoinConversation:
        join_instance = MagicMock()
        join_instance.json.return_value = '{"conversation_id":"test_conv"}'
        MockJoinConversation.return_value = join_instance

        with patch('aiohttp.ClientSession', return_value=mock_session):
            client = ChatClient(base_url="http://testserver")
            await client.connect(username="testuser")
            await client.join_conversation("test_conv")

            mock_ws.send_str.assert_awaited_once_with('{"conversation_id":"test_conv"}')


@pytest.mark.asyncio
async def test_leave_conversation():
    mock_ws = AsyncMock()
    mock_ws.send_str = AsyncMock()

    mock_session = AsyncMock(ws_connect=AsyncMock(return_value=mock_ws))

    # Mock LeaveConversation
    with patch('rxchat.chat_events.LeaveConversation') as MockLeaveConversation:
        leave_instance = MagicMock()
        leave_instance.json.return_value = '{"conversation_id":"test_conv"}'
        MockLeaveConversation.return_value = leave_instance

        with patch('aiohttp.ClientSession', return_value=mock_session):
            client = ChatClient(base_url="http://testserver")
            await client.connect(username="testuser")
            await client.leave_conversation("test_conv")

            mock_ws.send_str.assert_awaited_once_with('{"conversation_id":"test_conv"}')


@pytest.mark.asyncio
async def test_send_plain_message():
    mock_ws = AsyncMock()
    mock_ws.send_str = AsyncMock()

    mock_session = AsyncMock(ws_connect=AsyncMock(return_value=mock_ws))

    with patch('rxchat.chat_events.Message') as MockMessage:
        message_instance = MagicMock()
        message_instance.json.return_value = '{"conversation_id":"test_conv","content":"Hi!"}'
        MockMessage.return_value = message_instance

        with patch('aiohttp.ClientSession', return_value=mock_session):
            client = ChatClient(base_url="http://testserver")
            await client.connect(username="testuser")
            await client.message("test_conv", "Hi!")

            mock_ws.send_str.assert_awaited_once_with('{"conversation_id":"test_conv","content":"Hi!"}')
