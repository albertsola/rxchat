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


def message_header(message: Message) -> rx.Component:
    return rx.vstack(
        rx.avatar(fallback=message.username[:3], radius="full"),
        rx.hstack(
            rx.popover.root(
                rx.popover.trigger(
                    rx.icon("clock", size=11)
                ),
                rx.popover.content(
                    rx.moment(message.timestamp)
                )
            ),
            rx.popover.root(
                rx.popover.trigger(
                    rx.icon("user", size=11)
                ),
                rx.popover.content(
                    message.username
                )
            )
        )
    )


def render_other_message(message: Message) -> rx.Component:
    return rx.hstack(
        message_header(message),
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
        background_color=rx.color("mauve", 2),
        padding="1em 0.5em",
    )


def navbar() -> rx.Component:
    return rx.hstack(
        rx.input(type="text", on_change=ChatState.set_username, value=ChatState.username, read_only=ChatState.connected, placeholder="Your username"),
        rx.select(
            ChatState.channels,
            on_change=ChatState.change_conversation,
            value=ChatState.conversation_id,
            read_only=~ChatState.connected
        ),
        rx.badge(f"Users: {ChatState.conversation_user_count}", variant="soft", high_contrast=True),
        rx.cond(
            ChatState.connected,
            rx.hstack(rx.badge("Connected"), rx.button("Disconnect", on_click=ChatState.disconnect)),
            rx.hstack(rx.badge("Disconnected"), rx.button("Connect", on_click=ChatState.connect))
        ),
        justify_content="space-between",
        align_items="center",
        width="100%",
        on_mount=ChatState.load_channels,
    )


def message_composer_old() -> rx.Component:
    return rx.hstack(
        rx.select(["welcome", "queries"], on_change=ChatState.change_conversation, value=ChatState.conversation_id),
        rx.input(name="content", on_change=ChatState.set_content, value=ChatState.content, width="100%"),
        rx.button("Send", disabled=~ChatState.connected, on_click=ChatState.send_message),
        width="100%",
    )


def message_composer() -> rx.Component:
    """The action bar to send a new message."""
    return rx.box(
        rx.center(
            rx.vstack(
                rx.form(
                    rx.hstack(
                        rx.input(
                            placeholder="Type something...",
                            name="content",
                            width=["15em", "20em", "45em", "50em", "50em", "50em"],
                        ),
                        rx.button(
                            rx.cond(
                                ChatState.processing,
                                rx.spinner(),
                                rx.text("Send"),
                            ),
                            type="submit",
                        ),
                        align_items="center",
                    ),
                    is_disabled=ChatState.processing,
                    on_submit=ChatState.send_message,
                    reset_on_submit=True,
                )


            ),

        ),
        position="sticky",
        bottom="0",
        left="0",
        padding_y="16px",
        backdrop_filter="auto",
        backdrop_blur="lg",
        border_top=f"1px solid {rx.color('mauve', 3)}",
        background_color=rx.color("mauve", 2),
        align_items="stretch",
        width="100%",
    )


def chat() -> rx.Component:
    return rx.box(
        navbar(),
        messages(),
        message_composer(),
        width="100%",
        min_hegiht="300px",
    )
