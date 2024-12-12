import pytest
from unittest.mock import MagicMock
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
    ws = MagicMock()

    # Mock WebSocketClientHandler
    handler = MagicMock(spec=WebSocketClientHandler)
    chat_server.users = {username: handler}

    await chat_server.handle_user_websocket(username, ws)

    # Assert user was added to the users dictionary
    assert username in chat_server.users
    assert chat_server.users[username] == handler

    # Verify that the handler is called
    handler.assert_called_once_with(chat_server)


@pytest.mark.asyncio
async def test_handle_user_disconnected(chat_server):
    """Test handling of a user disconnecting."""
    username = "test_user"
    conversation_id = "test_conversation"

    # Setup mock conversation
    conversation = MagicMock(spec=Conversation)
    conversation.usernames = [username]
    chat_server.conversations = {conversation_id: conversation}

    # Mock send_message
    chat_server.send_message = MagicMock()

    await chat_server.handle_user_disconnected(username)

    # Verify that the user was removed from the conversation
    assert username not in conversation.usernames

    # Verify send_message was called with the expected message
    chat_server.send_message.assert_called_once_with(
        Message(conversation_id=conversation_id, username="_system", content=f"User {username} disconnected.")
    )


@pytest.mark.asyncio
async def test_user_join(chat_server):
    """Test a user joining a conversation."""
    username = "test_user"
    conversation_id = "test_conversation"

    # Mock send_message
    chat_server.send_message = MagicMock()

    await chat_server.user_join(username, conversation_id)

    # Verify that the conversation exists and the user is added
    conversation = chat_server.conversations[conversation_id]
    assert username in conversation.usernames

    # Verify send_message was called with the expected message
    chat_server.send_message.assert_called_once_with(
        Message(conversation_id=conversation_id, username="_system", content=f"{username} joined the conversation.")
    )


@pytest.mark.asyncio
async def test_user_leave(chat_server):
    """Test a user leaving a conversation."""
    username = "test_user"
    conversation_id = "test_conversation"

    # Setup mock conversation
    conversation = MagicMock(spec=Conversation)
    conversation.usernames = [username]
    chat_server.conversations = {conversation_id: conversation}

    # Mock send_message
    chat_server.send_message = MagicMock()

    await chat_server.user_leave(username, conversation_id)

    # Verify that the user was removed from the conversation
    conversation.usernames.remove.assert_called_once_with(username)

    # Verify send_message was called with the expected message
    chat_server.send_message.assert_called_once_with(
        Message(conversation_id=conversation_id, username="_system", content=f"{username} left the conversation.")
    )


@pytest.mark.asyncio
async def test_send_message_raises_if_conversation_not_found(chat_server, mock_message):
    """Test send_message raises an exception if the conversation is not found."""
    chat_server.conversations = {}

    with pytest.raises(RuntimeError, match="Conversation .* not found"):
        await chat_server.send_message(mock_message)


@pytest.mark.asyncio
async def test_send_message_successful(chat_server, mock_message):
    """Test successful message sending to a conversation."""
    username = "test_user"
    conversation_id = "test_conversation"

    # Setup mock conversation and users
    conversation = MagicMock(spec=Conversation)
    conversation.usernames = [username]
    chat_server.conversations = {conversation_id: conversation}

    # Mock WebSocketClientHandler
    handler = MagicMock(spec=WebSocketClientHandler)
    chat_server.users = {username: handler}

    # Mock notify
    chat_server.notify = MagicMock()

    await chat_server.send_message(mock_message)

    # Verify that the message was added to the conversation
    conversation.add_message.assert_called_once_with(mock_message)

    # Verify that notify was called for each user in the conversation
    chat_server.notify.assert_called_once_with(username, mock_message)


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
