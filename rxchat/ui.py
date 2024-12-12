import reflex as rx
from .chat_events import Message
from .rxchat import State


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


def message_render(message: Message)->rx.Component:
    return rx.cond(
        State.username == message.username,
        render_own_message(message),
        render_other_message(message)
    )


def messages() -> rx.Component:
    return rx.vstack(
        rx.foreach(State.messages, message_render),
        width="100%",
    )


def navbar() -> rx.Component:
    return rx.hstack(
        rx.input(type="text", on_change=State.set_username, value=State.username),
        rx.cond(

            State.connected,
            rx.badge("Connected"),
            rx.hstack(rx.badge("Disconnected"), rx.button("Connect", on_click=State.connect))
        ),
        width="100%",
    )


def write_message() -> rx.Component:
    return rx.hstack(
        rx.select(["welcome", "queries"], on_change=State.set_conversation_id, value=State.conversation_id),
        rx.input(name="content", on_change=State.set_content, value=State.content),
        rx.button("Send", disabled=~State.connected, on_click=State.send_message),
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
