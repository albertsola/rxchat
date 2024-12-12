import pytest
from unittest.mock import MagicMock, AsyncMock
from rxchat.chat_server import ChatServer, WebSocketClientHandler, Conversation, Message


@pytest.fixture
def chat_server():
    """Fixture for creating a new ChatServer instance."""
    return ChatServer()


@pytest.fixture
def mock_websocket():
    """Fixture for mocking WebSocketClientHandler."""
    return MagicMock(spec=WebSocketClientHandler)


@pytest.fixture
def mock_message():
    """Fixture for creating a mock Message."""
    return MagicMock(spec=Message)


@pytest.mark.asyncio
async def test_handle_user_websocket(chat_server, mock_websocket):
    """Test handling of a user's websocket connection."""
    username = "test_user"
    ws = AsyncMock()
    ws.accept = AsyncMock()
    ws.receive_json.side_effect = []

    await chat_server.handle_user_websocket(username, ws)

    ws.accept.assert_awaited_once()

    handler: WebSocketClientHandler = chat_server.users[username]

    # Assert user was added to the users dictionary
    assert username in chat_server.users
    assert handler.ws == ws
    assert handler.username == username


@pytest.mark.asyncio
async def test_handle_user_disconnected(chat_server):
    """Test handling of a user disconnecting."""
    username = "test_user"
    conversation_id = "test_conversation"

    # Setup mock conversation
    conversation = AsyncMock(spec=Conversation)
    conversation.usernames = [username]
    chat_server.conversations = {conversation_id: conversation}

    # Mock send_message
    chat_server.send_message = AsyncMock()

    await chat_server.handle_user_disconnected(username)

    # Verify that the user was removed from the conversation
    assert username not in conversation.usernames

    # Verify send_message was called with the expected message
    chat_server.send_message.assert_called_once_with(
        Message(
            conversation_id=conversation_id,
            username="_system",
            content=f"User {username} disconnected.",
        )
    )


@pytest.mark.asyncio
async def test_user_join(chat_server):
    """Test a user joining a conversation."""
    username = "test_user"
    conversation_id = "test_conversation"

    # Mock send_message
    chat_server.send_message = AsyncMock()

    await chat_server.user_join(username, conversation_id)

    # Verify that the conversation exists and the user is added
    conversation = chat_server.conversations[conversation_id]
    assert username in conversation.usernames

    # Verify send_message was called with the expected message
    chat_server.send_message.assert_called_once_with(
        Message(
            conversation_id=conversation_id,
            username="_system",
            content=f"{username} joined the conversation.",
        )
    )


@pytest.mark.asyncio
async def test_user_leave(chat_server):
    """Test a user leaving a conversation."""

    conversation_id = "test_conversation"

    conversation = Conversation()

    username = "test_user"
    user_handler = AsyncMock(spec=WebSocketClientHandler)
    user_handler.username = username
    conversation.usernames.append(username)

    other_user = "other_user"
    other_user_handler = AsyncMock(spec=WebSocketClientHandler)
    other_user_handler.username = other_user
    conversation.usernames.append(other_user)

    chat_server.conversations = {conversation_id: conversation}

    chat_server.users[username] = user_handler
    chat_server.users[other_user] = user_handler

    chat_server.send_message = AsyncMock()

    await chat_server.user_leave(username, conversation_id)
    assert (
        username not in chat_server.conversations[conversation_id].usernames
    ), f"Username {username} should not be in the conversation"

    # Verify send_message was called with the expected message
    chat_server.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_message_raises_if_conversation_not_found(chat_server):
    """Test send_message raises an exception if the conversation is not found."""
    chat_server.conversations = {}

    message = Message(conversation_id="cid", username="test_user", content="content")

    with pytest.raises(RuntimeError, match="Conversation .* not found"):
        await chat_server.send_message(message)


@pytest.mark.asyncio
async def test_send_message_successful(chat_server):
    """Test successful message sending to a conversation."""
    username = "test_user"
    conversation_id = "test_conversation"

    message = Message(
        conversation_id=conversation_id, username="test_user", content="content"
    )

    # Setup mock conversation and users
    conversation = Conversation()
    conversation.usernames = [username]
    chat_server.conversations = {conversation_id: conversation}

    # Mock WebSocketClientHandler
    handler = AsyncMock(spec=WebSocketClientHandler)
    chat_server.users = {username: handler}

    # Mock notify
    chat_server.notify = AsyncMock()

    await chat_server.send_message(message)

    # Verify that notify was called for each user in the conversation
    chat_server.notify.assert_awaited_once_with(username, message)


@pytest.mark.asyncio
async def test_notify_does_not_send_message_if_user_not_found(chat_server):
    """Test notify does not send message if the user is not found."""
    username = "test_user"
    message = MagicMock(spec=Message)

    # Ensure the user is not in the users dictionary
    chat_server.users = {}

    await chat_server.notify(username, message)

    # Assert that send was not called
    chat_server.users.get(username, MagicMock()).send.assert_not_called()
