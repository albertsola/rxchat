import pytest
import httpx
import aiohttp
from .rest_client import ChatRestClient
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def chat_client():
    """Fixture to initialize the ChatAPIClient."""
    base_url = "http://testserver"
    client = ChatRestClient(base_url=base_url)
    return client


def mock_response(data: dict|None = None, status_code=200):
    mock_response = AsyncMock()
    mock_response.json.return_value = data
    mock_response.raise_for_status = AsyncMock()
    return AsyncMock(__aenter__=AsyncMock(return_value=mock_response), status_code=status_code)


@pytest.mark.asyncio
async def test_get_conversations(chat_client: ChatRestClient, mocker):
    """Test fetching the list of conversations."""
    response_data = [{"id": "123", "users_count": 5}, {"id": "456", "users_count": 2}]

    # Create a mock response object

    # Mock aiohttp.ClientSession.get
    mocker.patch(
        "aiohttp.ClientSession.get",
        return_value=mock_response(response_data),
    )

    result = await chat_client.get_conversations()

    assert result == response_data


@pytest.mark.asyncio
async def test_join_conversation(chat_client: ChatRestClient, mocker):
    """Test joining a conversation."""
    mocker.patch("aiohttp.ClientSession.post", return_value=mock_response())

    username = "test_user"
    conversation_id = "123"

    await chat_client.join_conversation(username=username, conversation_id=conversation_id)
    aiohttp.ClientSession.post.assert_called_once()


@pytest.mark.asyncio
async def test_leave_conversation(chat_client: ChatRestClient, mocker):
    """Test leaving a conversation."""
    mocker.patch("aiohttp.ClientSession.post", return_value=mock_response())

    username = "test_user"
    conversation_id = "123"

    await chat_client.leave_conversation(username=username, conversation_id=conversation_id)
    aiohttp.ClientSession.post.assert_called_once()


@pytest.mark.asyncio
async def test_send_message(chat_client: ChatRestClient, mocker):
    """Test leaving a conversation."""
    mocker.patch("aiohttp.ClientSession.put", return_value=mock_response(status_code=200))

    username = "test_user"
    conversation_id = "123"
    content = "Hello World"

    await chat_client.send_message(username=username, conversation_id=conversation_id, content=content)
    aiohttp.ClientSession.put.assert_called_once()
