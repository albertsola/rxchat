from typing import Literal, Annotated, Union
from pydantic import Field
import reflex as rx

from datetime import datetime


class JoinConversation(rx.Model):
    event: Literal["conversation.join"] = "conversation.join"
    conversation_id: str


class LeaveConversation(rx.Model):
    event: Literal["conversation.leave"] = "conversation.leave"
    conversation_id: str


class Message(rx.Model):
    event: Literal["conversation.message"] = "conversation.message"
    datetime: datetime = datetime.now()
    conversation_id: str | None = None
    username: str
    message: str


class Conversation(rx.Model):
    usernames: list[str]
    messages: [Message] = []

    def add_message(self, message: Message):
        if message.username not in self.usernames:
            self.usernames.append(message.username)
        self.messages.append(message)

    def remove(self, username: str):
        self.usernames.remove(username)


ClientMessage: Annotated[
    Union[JoinConversation, LeaveConversation, Message],
    Field(discriminator="event")
]

ServerMessage: Message
