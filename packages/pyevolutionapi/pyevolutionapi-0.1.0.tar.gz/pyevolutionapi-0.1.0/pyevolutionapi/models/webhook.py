"""
Models for Webhook and Events configuration.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field, HttpUrl

from .base import BaseModel, BaseResponse


class WebhookEvent(str, Enum):
    """Available webhook events."""

    APPLICATION_STARTUP = "APPLICATION_STARTUP"
    QRCODE_UPDATED = "QRCODE_UPDATED"
    MESSAGES_SET = "MESSAGES_SET"
    MESSAGES_UPSERT = "MESSAGES_UPSERT"
    MESSAGES_UPDATE = "MESSAGES_UPDATE"
    MESSAGES_DELETE = "MESSAGES_DELETE"
    SEND_MESSAGE = "SEND_MESSAGE"
    CONTACTS_SET = "CONTACTS_SET"
    CONTACTS_UPSERT = "CONTACTS_UPSERT"
    CONTACTS_UPDATE = "CONTACTS_UPDATE"
    PRESENCE_UPDATE = "PRESENCE_UPDATE"
    CHATS_SET = "CHATS_SET"
    CHATS_UPSERT = "CHATS_UPSERT"
    CHATS_UPDATE = "CHATS_UPDATE"
    CHATS_DELETE = "CHATS_DELETE"
    GROUPS_UPSERT = "GROUPS_UPSERT"
    GROUP_UPDATE = "GROUP_UPDATE"
    GROUP_PARTICIPANTS_UPDATE = "GROUP_PARTICIPANTS_UPDATE"
    CONNECTION_UPDATE = "CONNECTION_UPDATE"
    LABELS_EDIT = "LABELS_EDIT"
    LABELS_ASSOCIATION = "LABELS_ASSOCIATION"
    CALL = "CALL"
    TYPEBOT_START = "TYPEBOT_START"
    TYPEBOT_CHANGE_STATUS = "TYPEBOT_CHANGE_STATUS"


class WebhookConfig(BaseModel):
    """Model for webhook configuration."""

    enabled: bool = Field(True, description="Whether webhook is enabled")
    url: HttpUrl = Field(..., description="Webhook URL to receive events")
    webhook_by_events: bool = Field(
        False, alias="byEvents", description="Send separate webhooks per event"
    )
    webhook_base64: bool = Field(True, alias="base64", description="Encode media in base64")
    headers: Optional[Dict[str, str]] = Field(
        None, description="Custom headers for webhook requests"
    )
    events: Optional[List[WebhookEvent]] = Field(None, description="Events to listen for")

    def add_event(self, event: WebhookEvent) -> None:
        """Add an event to the webhook configuration."""
        if self.events is None:
            self.events = []
        if event not in self.events:
            self.events.append(event)

    def remove_event(self, event: WebhookEvent) -> None:
        """Remove an event from the webhook configuration."""
        if self.events and event in self.events:
            self.events.remove(event)

    def set_auth_header(self, token: str, header_name: str = "Authorization") -> None:
        """Set authentication header."""
        if self.headers is None:
            self.headers = {}
        self.headers[header_name] = f"Bearer {token}"


class WebsocketConfig(BaseModel):
    """Model for WebSocket configuration."""

    enabled: bool = Field(True, description="Whether WebSocket is enabled")
    events: Optional[List[WebhookEvent]] = Field(None, description="Events to listen for")


class RabbitmqConfig(BaseModel):
    """Model for RabbitMQ configuration."""

    enabled: bool = Field(True, description="Whether RabbitMQ is enabled")
    events: Optional[List[WebhookEvent]] = Field(None, description="Events to listen for")


class SqsConfig(BaseModel):
    """Model for AWS SQS configuration."""

    enabled: bool = Field(True, description="Whether SQS is enabled")
    events: Optional[List[WebhookEvent]] = Field(None, description="Events to listen for")


class EventPayload(BaseModel):
    """Model for event payload received via webhook."""

    event: WebhookEvent = Field(..., description="Event type")
    instance: str = Field(..., description="Instance name")
    data: Dict[str, Any] = Field(..., description="Event data")
    timestamp: Optional[int] = Field(None, description="Event timestamp")

    # Connection update specific
    state: Optional[str] = None
    status_reason: Optional[int] = Field(None, alias="statusReason")

    # Message specific
    message: Optional[Dict[str, Any]] = None
    key: Optional[Dict[str, Any]] = None

    # QR Code specific
    qrcode: Optional[Dict[str, str]] = None

    @property
    def is_connection_event(self) -> bool:
        """Check if this is a connection event."""
        return self.event == WebhookEvent.CONNECTION_UPDATE

    @property
    def is_message_event(self) -> bool:
        """Check if this is a message event."""
        return self.event in [
            WebhookEvent.MESSAGES_UPSERT,
            WebhookEvent.MESSAGES_UPDATE,
            WebhookEvent.MESSAGES_DELETE,
            WebhookEvent.SEND_MESSAGE,
        ]


class WebhookResponse(BaseResponse):
    """Response for webhook operations."""

    webhook: Optional[WebhookConfig] = None
    websocket: Optional[WebsocketConfig] = None
    rabbitmq: Optional[RabbitmqConfig] = None
    sqs: Optional[SqsConfig] = None

    @property
    def is_configured(self) -> bool:
        """Check if any event handler is configured."""
        return any(
            [
                self.webhook and self.webhook.enabled,
                self.websocket and self.websocket.enabled,
                self.rabbitmq and self.rabbitmq.enabled,
                self.sqs and self.sqs.enabled,
            ]
        )
