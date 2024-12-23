import reflex as rx
from reflex_rxchat.server.events import (
    EventType,
    Message,
    EventUserJoinConversation,
    EventUserLeaveConversation,
    ResponseJoinConversation,
    ServerMessage,
)
from reflex import Component
from .state import ChatState


class ConversationMessagesComponent(Component):

    @classmethod
    def _message_header(cls, message: Message, *children, **props) -> Component:
        return rx.vstack(
            rx.cond(
                message.username,
                rx.avatar(fallback=message.username[0:3], radius="full"),
            ),
            rx.hstack(
                rx.popover.root(
                    rx.popover.trigger(rx.icon("clock", size=11)),
                    rx.popover.content(rx.moment(message.timestamp)),
                ),
                rx.popover.root(
                    rx.popover.trigger(rx.icon("user", size=11)),
                    rx.popover.content(message.username),
                ),
            ),
        )

    @classmethod
    def own_message(cls, message: Message, *children, **props) -> Component:
        return rx.card(message.content, margin_left="auto")

    @classmethod
    def participant_message(cls, message: Message, *children, **props) -> Component:
        return rx.hstack(
            cls._message_header(message),
            rx.card(message.content),
        )

    @classmethod
    def message(cls, message: Message, *children, **props) -> Component:
        return rx.cond(
            ChatState.username == message.username,
            cls.own_message(message),
            cls.participant_message(message),
        )

    @classmethod
    def join(cls, event: EventUserJoinConversation, *children, **props) -> Component:
        return rx.hstack(
            rx.icon("log-in"),
            rx.card(
                rx.text(rx.text.strong(event.username), " joined the conversation"),
                align="center",
                width="100%",
            ),
            width="100%",
        )

    @classmethod
    def leave(cls, event: EventUserLeaveConversation, *children, **props) -> Component:
        return rx.hstack(
            rx.icon("log-out"),
            rx.card(
                rx.text(rx.text.strong(event.username), " left the conversation"),
                align="center",
                width="100%",
            ),
            width="100%",
        )

    @classmethod
    def join_response(
        cls, event: ResponseJoinConversation, *children, **props
    ) -> Component:
        return rx.hstack(
            rx.card(
                rx.text(
                    rx.text.strong("You"),
                    " have joined ",
                    rx.text.strong(event.conversation_id),
                ),
                align="center",
            ),
            justify="between",
            width="100%",
        )

    @classmethod
    def event(cls, event: ServerMessage, *args) -> Component:
        return rx.match(
            event.event,
            (EventType.CONVERSATION_MESSAGE, cls.message(event)),
            (EventType.EVENT_CONVERSATION_JOIN, cls.join(event)),
            (EventType.EVENT_CONVERSATION_LEAVE, cls.leave(event)),
            (EventType.RESPONSE_CONVERSATION_JOIN, cls.join_response(event)),
            (rx.text(f"Unknown event type {event.event}")),
        )

    @classmethod
    def create(cls, *children, **props) -> Component:
        return rx.vstack(
            rx.foreach(ChatState.messages, cls.event),
            width="100%",
            background_color=rx.color("mauve", 2),
            padding="1em 0.5em",
        )


class NavbarComponent(Component):
    @classmethod
    def create(cls, *children, **props) -> Component:
        return rx.hstack(
            rx.input(
                type="text",
                on_change=ChatState.set_username,
                value=ChatState.username,
                read_only=ChatState.connected,
                placeholder="Your username",
            ),
            rx.select(
                ChatState.conversations,
                on_change=ChatState.change_conversation,
                value=ChatState.conversation_id,
                read_only=~ChatState.connected,
            ),
            rx.badge(
                f"Users: {ChatState.conversation_user_count}",
                variant="soft",
                high_contrast=True,
            ),
            rx.cond(
                ChatState.connected,
                rx.hstack(
                    rx.badge("Connected"),
                    rx.button("Disconnect", on_click=ChatState.disconnect),
                ),
                rx.hstack(
                    rx.badge("Disconnected"),
                    rx.button("Connect", on_click=ChatState.connect),
                ),
            ),
            justify_content="space-between",
            align_items="center",
            width="100%",
            on_mount=ChatState.load_conversations,
        )


class ConversationInputComponent(Component):

    @classmethod
    def create(cls, *childre, **props) -> Component:
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
                                disabled=ChatState.processing | ~ChatState.connected,
                            ),
                            align_items="center",
                        ),
                        is_disabled=ChatState.processing | ~ChatState.connected,
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


class ConversationUsersComponent(Component):

    @classmethod
    def render_username(cls, username, *args):
        return rx.badge(username)

    @classmethod
    def create(cls, *children, **props) -> Component:
        return rx.hstack(
            rx.text(f"Users: {ChatState.conversation_user_count}"),
            rx.flex(
                rx.foreach(ChatState.conversation_users, cls.render_username),
                spacing="1",
            ),
            background_color=rx.color("mauve", 2),
        )


class ConversationComponent(Component):
    @classmethod
    def create(cls, *children, **props) -> Component:
        return rx.box(
            NavbarComponent.create(),
            ConversationMessagesComponent.create(),
            ConversationUsersComponent.create(),
            ConversationInputComponent.create(),
            width="100%",
            min_height="300px",
        )


conversation = ConversationComponent.create
