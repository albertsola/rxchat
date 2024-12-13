import reflex as rx

from rxchat.client import ChatClient
from rxchat.server import Message


class ChatState(rx.State):
    """The app state."""

    _chat: ChatClient | None = None
    connected: bool = False
    channels: list[str] = ["Welcome", "Jokes", "Tech"]

    messages: list[Message] = []
    conversation_id: str = "Welcome"
    content: str = ""
    username: str = ""
    processing: bool = False

    @rx.event(background=True)
    async def connect(self):
        try:
            async with self:
                if self.username.__len__() < 5:
                    return rx.toast.error("Your username has to be at least 5 characters long")
            frontend_scheme: str = self.router.page.host.split(":")[0]
            backend_hostname: str = self.router.headers.host
            base_url: str = f"{frontend_scheme}://{backend_hostname}/"
            print(f"{base_url=}")
            async with self:
                self._chat = ChatClient(base_url=base_url)
                await self._chat.connect(self.username)
                await self._chat.join_conversation(self.conversation_id)
                self.connected = True
            async for m in self._chat.receive():
                async with self:
                    self.messages.append(m)
        except Exception as ex:
            async with self:
                return rx.toast.error(f"Error: {ex}")

        finally:
            async with self:
                self._chat = None
                self.connected = False

    @rx.event
    async def change_conversation(self, conversation_id: str):
        assert self._chat is not None, "ChatState._chat needs to be initialized to change_conversation"
        await self._chat.leave_conversation(self.conversation_id)
        self.conversation_id = conversation_id
        await self._chat.join_conversation(self.conversation_id)

    @rx.event
    async def join_conversation(self, conversation_id: str):
        assert self._chat is not None
        await self._chat.join_conversation(conversation_id)

    @rx.event
    async def leave_conversation(self, conversation_id: str):
        assert self._chat is not None
        await self._chat.leave_conversation(conversation_id)

    @rx.event
    async def send_message(self, form_data: dict):
        assert self._chat is not None, "ChatState._chat needs to be initialized to send a message"
        self.processing = True
        self.content = form_data['content']
        if not self.content:
            return
        await self._chat.send_message(self.conversation_id, self.content)
        self.content = ""
        self.processing = False

    @rx.event
    async def disconnect(self):
        await self._chat.disconnect()
