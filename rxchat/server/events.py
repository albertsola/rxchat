from typing import Literal, Union

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
    timestamp: datetime = datetime.now()
    conversation_id: str | None = None
    username: str
    content: str


class Conversation(rx.Model):
    usernames: list[str] = []
    messages: list[Message] = []

    def add_message(self, message: Message):
        if message.username not in self.usernames:
            self.usernames.append(message.username)
        self.messages.append(message)

    def remove_user(self, username: str):
        self.usernames.remove(username)


ClientMessage = Union[JoinConversation, LeaveConversation, Message]

ServerMessage = Union[Message]
