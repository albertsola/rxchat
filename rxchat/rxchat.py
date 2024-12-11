"""Welcome to Reflex! This file outlines the steps to create a basic app."""
import reflex as rx

from rxconfig import config
from rxchat.chat_client import ChatClient
from rxchat.chat_events import Message


class State(rx.State):
    """The app state."""
    _chat: ChatClient | None = None
    connected: bool = False

    messages: list[Message] = []

    @rx.event(background=True)
    async def connect(self):
        try:
            self._chat = ChatClient()
            self._chat.connect()
            async with self:
                self.connected = True
            async for m in self._chat.receive():
                async with self:
                    self.messages.append(m)
        finally:
            self._chat = None
            async with self:
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
    async def message(self, conversation_id: str, content: str):
        assert self._chat is not None
        await self._chat.message(conversation_id, content)





def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
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
