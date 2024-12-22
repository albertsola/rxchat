from typing import Literal, Union

import reflex as rx

from datetime import datetime


class RequestJoinConversation(rx.Model):
    event: Literal["request.conversation.join"] = "request.conversation.join"
    conversation_id: str


class ResponseJoinConversation(rx.Model):
    event: Literal["response.conversation.join"] = "response.conversation.join"
    conversation_id: str
    users: list[str]


class RequestLeaveConversation(rx.Model):
    event: Literal["request.conversation.leave"] = "request.conversation.leave"
    conversation_id: str


class EventUserJoinConversation(rx.Model):
    event: Literal["event.conversation.join"] = "event.conversation.join"
    username: str
    conversation_id: str


class EventUserLeaveConversation(rx.Model):
    event: Literal["event.conversation.leave"] = "event.conversation.leave"
    username: str
    conversation_id: str


class Message(rx.Model):
    event: Literal["conversation.message"] = "conversation.message"
    timestamp: datetime = datetime.now()
    conversation_id: str | None = None
    username: str
    content: str


ClientMessage = Union[RequestJoinConversation, RequestLeaveConversation, Message]

ServerMessage = Union[Message, EventUserJoinConversation, EventUserLeaveConversation, ResponseJoinConversation]
