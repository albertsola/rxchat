import uuid
import reflex as rx

from rxchat.client import ChatClient
from rxchat.server import Message


class ChatState(rx.State):
    """The app state."""

    _chat: ChatClient | None = None
    connected: bool = False

    messages: list[Message] = []
    conversation_id: str = "welcome"
    content: str = ""
    username: str = str(uuid.uuid4())

    @rx.event(background=True)
    async def connect(self):
        try:
            frontend_scheme = self.router.page.host.split(":")[0]
            backend_hostname = self.router.headers.host
            base_url: str = f"{frontend_scheme}://{backend_hostname}/"
            print(f"{base_url=}")
            async with self:
                self._chat = ChatClient(base_url=base_url)
                await self._chat.connect(self.username)
                await self._chat.join_conversation("welcome")
                self.connected = True
            async for m in self._chat.receive():
                async with self:
                    self.messages.append(m)
        finally:
            async with self:
                self._chat = None
                self.connected = False

    @rx.event
    async def join_conversation(self, conversation_id: str):
        assert self._chat is not None
        await self._chat.join_conversation(conversation_id)

    @rx.event
    async def leave_conversation(self, conversation_id: str):
        assert self._chat is not None
        await self._chat.leave_conversation(conversation_id)

    @rx.event
    async def send_message(self):
        if not self.content:
            return
        ret = await self._chat.send_message(self.conversation_id, self.content)
        self.content = ""
        return ret
