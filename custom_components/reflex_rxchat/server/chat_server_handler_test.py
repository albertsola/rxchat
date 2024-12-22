import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from reflex_rxchat.server.websocket_handler import WebSocketClientHandler
from reflex_rxchat.server.events import Message
from starlette.websockets import WebSocketState


@pytest.mark.asyncio
async def test_handler_accepts_websocket_and_closes_on_cancel():
    # Mock websocket and chat_state
    ws = AsyncMock()
    ws.state = WebSocketState.CONNECTED
    chat_state = AsyncMock()
    handler = WebSocketClientHandler(ws, username="testuser")
    chat_state.get_users = MagicMock(return_value={"testuser": handler})

    # Make ws.receive_json() raise asyncio.CancelledError after first call
    ws.receive_json.side_effect = asyncio.CancelledError
    # Run the handler and ensure it handles cancellation
    await handler(chat_state)
    ws.receive_json.assert_awaited_once()
    ws.accept.assert_awaited_once()
    ws.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_handler_conversation_message():
    ws = AsyncMock()
    ws.state = WebSocketState.CONNECTED
    chat_state = AsyncMock()
    handler = WebSocketClientHandler(ws, username="alice")
    chat_state.get_users = MagicMock(return_value={"alice": handler})

    # Simulate receiving a "conversation.message" event once, then stop
    ws.receive_json.side_effect = [
        {
            "event": "conversation.message",
            "conversation_id": 123,
            "username": "alice",
            "content": "Hello",
        },
        asyncio.CancelledError,
    ]


    await handler(chat_state)

    # Ensure ws was accepted
    ws.accept.assert_awaited_once()

    # chat_state.send_message should have been called with a message that has username set to "alice"
    assert chat_state.send_message.await_count == 1
    sent_msg = chat_state.send_message.await_args[0][0]
    assert sent_msg.username == "alice"
    assert sent_msg.event == "conversation.message"
    ws.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_handler_unknown_event():
    ws = AsyncMock()
    ws.state = WebSocketState.CONNECTED
    chat_state = AsyncMock()
    chat_state.get_users = MagicMock(return_value={})

    # Simulate an unknown event
    ws.receive_json.side_effect = [{"event": "unknown.event"}, asyncio.CancelledError]
    handler = WebSocketClientHandler(ws, username="david")
    with pytest.raises(RuntimeError) as exc_info:
        await handler(chat_state)
    assert "Server received unknown message" in str(exc_info.value)

@pytest.mark.asyncio
async def test_handler_unknown_message():
    ws = AsyncMock()
    ws.state = WebSocketState.CONNECTED
    chat_state = AsyncMock()
    chat_state.get_users = MagicMock(return_value={})

    # Simulate an unknown event
    ws.receive_json.side_effect = ["asdasdfasfsd", asyncio.CancelledError]
    handler = WebSocketClientHandler(ws, username="david")
    with pytest.raises(RuntimeError) as exc_info:
        await handler(chat_state)
    assert "Server received malformed message. " in str(exc_info.value)


@pytest.mark.asyncio
async def test_send_method():
    ws = AsyncMock()
    handler = WebSocketClientHandler(ws, username="eve")

    # Create a client message
    msg = Message(
        username="testusername", conversation_id="eve", content="Message content"
    )

    await handler.send(msg)
    ws.send_text.assert_awaited_once_with(msg.json())


@pytest.mark.asyncio
async def test_receive_method():
    ws = AsyncMock()
    # Simulate two messages, then raise CancelledError to break out of loop
    ws.receive_json.side_effect = [
        {
            "event": "conversation.message",
            "conversation_id": 123,
            "username": "test user",
            "content": "Hello",
        },
        {
            "event": "conversation.message",
            "conversation_id": 123,
            "username": "test user",
            "content": "world",
        },
        asyncio.CancelledError,
    ]

    handler = WebSocketClientHandler(ws, username="frank")

    messages = []
    try:
        async for msg in handler.receive():
            messages.append(msg)
    except asyncio.CancelledError:
        pass  # This simulates the external break in production

    # Check that we got our two messages
    assert len(messages) == 2
    assert messages[0].event == "conversation.message"
    assert messages[1].event == "conversation.message"
