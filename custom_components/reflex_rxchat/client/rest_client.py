import aiohttp
from typing import List, Dict


class ChatRestClient:
    def __init__(self, base_url: str):
        """Initializes the client with the base URL of the API."""
        self.base_url = base_url

    async def get_conversations(self) -> List[Dict]:
        """Fetches the list of conversations."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/conversations") as response:
                response.raise_for_status()
                return await response.json()

    async def join_conversation(self, username: str, conversation_id: str):
        """Allows a user to join a specific conversation."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/conversation/{conversation_id}/join",
                params={"username": username},
            ) as response:
                response.raise_for_status()

    async def leave_conversation(self, username: str, conversation_id: str):
        """Allows a user to leave a specific conversation."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/conversation/{conversation_id}/leave",
                params={"username": username},
            ) as response:
                response.raise_for_status()

    async def send_message(self, username: str, conversation_id: str, content: str):
        """Allows a user to send a message in a specific conversation."""
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{self.base_url}/conversation/{conversation_id}/message",
                params={"username": username, "content": content},
            ) as response:
                response.raise_for_status()
