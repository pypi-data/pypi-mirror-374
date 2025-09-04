"""
Data models for Evolution API resources.
"""

from .base import BaseModel, BaseResponse
from .chat import Chat, Contact, PrivacySettings, ProfilePicture
from .group import Group, GroupCreate, GroupParticipant, GroupResponse, GroupUpdate
from .instance import ConnectionState, Instance, InstanceCreate, InstanceResponse
from .message import (
    AudioMessage,
    ContactMessage,
    LocationMessage,
    MediaMessage,
    MessageResponse,
    MessageStatus,
    ReactionMessage,
    StickerMessage,
    TextMessage,
)
from .webhook import WebhookConfig, WebhookEvent, WebhookResponse

__all__ = [
    # Base
    "BaseModel",
    "BaseResponse",
    # Instance
    "Instance",
    "InstanceCreate",
    "InstanceResponse",
    "ConnectionState",
    # Messages
    "TextMessage",
    "MediaMessage",
    "LocationMessage",
    "ContactMessage",
    "ReactionMessage",
    "AudioMessage",
    "StickerMessage",
    "MessageResponse",
    "MessageStatus",
    # Groups
    "Group",
    "GroupCreate",
    "GroupUpdate",
    "GroupParticipant",
    "GroupResponse",
    # Chat
    "Chat",
    "Contact",
    "ProfilePicture",
    "PrivacySettings",
    # Webhook
    "WebhookConfig",
    "WebhookEvent",
    "WebhookResponse",
]
