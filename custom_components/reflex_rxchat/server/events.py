from typing import Literal, Union

import reflex as rx

from datetime import datetime
from enum import StrEnum


class EventType(StrEnum):
    REQUEST_CONVERSATION_JOIN = "request.conversation.join"
    RESPONSE_CONVERSATION_JOIN = "response.conversation.join"
    REQUEST_CONVERSATION_LEAVE = "request.conversation.leave"
    EVENT_CONVERSATION_JOIN = "event.conversation.join"
    EVENT_CONVERSATION_LEAVE = "event.conversation.leave"
    CONVERSATION_MESSAGE = "conversation.message"


class ResponseJoinConversation(rx.Model):
    event: Literal[EventType.RESPONSE_CONVERSATION_JOIN] = EventType.RESPONSE_CONVERSATION_JOIN
    conversation_id: str
    users: list[str]


class RequestJoinConversation(rx.Model):
    event: Literal[EventType.REQUEST_CONVERSATION_JOIN] = EventType.REQUEST_CONVERSATION_JOIN
    conversation_id: str


class RequestLeaveConversation(rx.Model):
    event: Literal[EventType.REQUEST_CONVERSATION_LEAVE] = EventType.REQUEST_CONVERSATION_LEAVE
    conversation_id: str


class EventUserJoinConversation(rx.Model):
    event: Literal[EventType.EVENT_CONVERSATION_JOIN] = EventType.EVENT_CONVERSATION_JOIN
    username: str
    conversation_id: str


class EventUserLeaveConversation(rx.Model):
    event: Literal[EventType.EVENT_CONVERSATION_LEAVE] = EventType.EVENT_CONVERSATION_LEAVE
    username: str
    conversation_id: str


class Message(rx.Model):
    event: Literal[EventType.CONVERSATION_MESSAGE] = EventType.CONVERSATION_MESSAGE
    timestamp: datetime = datetime.now()
    conversation_id: str | None = None
    username: str
    content: str


ClientMessage = Union[RequestJoinConversation, RequestLeaveConversation, Message]

ServerMessage = Union[
    Message,
    EventUserJoinConversation,
    EventUserLeaveConversation,
    ResponseJoinConversation,
]
