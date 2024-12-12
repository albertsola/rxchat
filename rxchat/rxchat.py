"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config
from rxchat.chat_client import ChatClient
from rxchat.chat_events import Message
from rxchat.api import router
import uuid


class State(rx.State):
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
            print(self.router.headers)
            hostname: str = f"http://{self.router.headers.host}/"
            print(hostname)
            async with self:
                self._chat = ChatClient(base_url=hostname)
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
        ret = await self.message(self.conversation_id, self.content)
        self.content = ""
        return ret

    @rx.event
    async def message(self, conversation_id: str, content: str):
        assert self._chat is not None
        await self._chat.message(conversation_id, content)


def index() -> rx.Component:
    from .ui import chat
    # Welcome Page (Index)
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            chat(),
            rx.heading("Welcome to Reflex!", size="9"),
            rx.text(
                "Get started by editing ",
                rx.code(f"{config.app_name}/{config.app_name}.py"),
                size="5",
            ),
            rx.link(
                rx.button("Check out our docs!"),
                href="https://reflex.dev/docs/getting-started/introduction/",
                is_external=True,
            ),
            spacing="5",
            justify="center",
            min_height="85vh",
        ),
        rx.logo(),
    )


app = rx.App()
app.add_page(index)
app.api.include_router(router)
