import reflex as rx
from rxchat.server.events import Message
from .state import ChatState


def render_own_message(message: Message) -> rx.Component:
    return rx.hstack(
        rx.card(
            message.content,
            margin_left="auto"
        ),
        width="100%",
    )


def render_other_message(message: Message) -> rx.Component:
    return rx.hstack(
        rx.badge(message.username),
        rx.card(
            message.content,
        )
    )


def message_render(message: Message) -> rx.Component:
    return rx.cond(
        ChatState.username == message.username,
        render_own_message(message),
        render_other_message(message)
    )


def messages() -> rx.Component:
    return rx.vstack(
        rx.foreach(ChatState.messages, message_render),
        width="100%",
    )


def navbar() -> rx.Component:
    return rx.hstack(
        rx.input(type="text", on_change=ChatState.set_username, value=ChatState.username),
        rx.cond(

            ChatState.connected,
            rx.badge("Connected"),
            rx.hstack(rx.badge("Disconnected"), rx.button("Connect", on_click=ChatState.connect))
        ),
        width="100%",
    )


def write_message() -> rx.Component:
    return rx.hstack(
        rx.select(["welcome", "queries"], on_change=ChatState.set_conversation_id, value=ChatState.conversation_id),
        rx.input(name="content", on_change=ChatState.set_content, value=ChatState.content),
        rx.button("Send", disabled=~ChatState.connected, on_click=ChatState.send_message),
        width="100%",
    )


def chat() -> rx.Component:
    return rx.box(
        navbar(),
        messages(),
        write_message(),
        width="100%",
        min_hegiht="300px",
    )
