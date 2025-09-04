"""
Models for Chat operations and profiles.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import BaseModel, BaseResponse, TimestampedModel


class PresenceType(str, Enum):
    """Types of presence."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    COMPOSING = "composing"
    RECORDING = "recording"
    PAUSED = "paused"


class PrivacyOption(str, Enum):
    """Privacy setting options."""

    ALL = "all"
    CONTACTS = "contacts"
    CONTACT_BLACKLIST = "contact_blacklist"
    NONE = "none"
    MATCH_LAST_SEEN = "match_last_seen"


class Contact(TimestampedModel):
    """Model for a contact."""

    id: str = Field(..., description="Contact JID")
    name: Optional[str] = Field(None, description="Contact name")
    notify: Optional[str] = Field(None, description="Contact notify name")

    # Profile info
    profile_pic_url: Optional[str] = Field(None, alias="profilePicUrl")
    status: Optional[str] = Field(None, description="Contact status message")

    # WhatsApp info
    is_business: Optional[bool] = Field(None, alias="isBusiness")
    is_enterprise: Optional[bool] = Field(None, alias="isEnterprise")
    is_group: Optional[bool] = Field(None, alias="isGroup")
    is_my_contact: Optional[bool] = Field(None, alias="isMyContact")
    is_user: Optional[bool] = Field(None, alias="isUser")
    is_wa_contact: Optional[bool] = Field(None, alias="isWAContact")

    # Phone info
    phone: Optional[str] = None
    short_name: Optional[str] = Field(None, alias="shortName")
    push_name: Optional[str] = Field(None, alias="pushName")

    # Business info
    business_profile: Optional[Dict[str, Any]] = Field(None, alias="businessProfile")

    @property
    def jid(self) -> str:
        """Get the contact JID in the correct format."""
        if "@" not in self.id:
            return f"{self.id}@s.whatsapp.net"
        return self.id


class Chat(TimestampedModel):
    """Model for a chat."""

    id: str = Field(..., description="Chat JID")
    name: Optional[str] = Field(None, description="Chat name")

    # Chat state
    unread_count: Optional[int] = Field(None, alias="unreadCount")
    archived: Optional[bool] = False
    pinned: Optional[bool] = False
    mute_expiration: Optional[int] = Field(None, alias="muteExpiration")

    # Last message info
    last_message_time: Optional[int] = Field(None, alias="lastMessageTime")
    last_message: Optional[Dict[str, Any]] = Field(None, alias="lastMessage")

    # Ephemeral settings
    ephemeral_expiration: Optional[int] = Field(None, alias="ephemeralExpiration")
    ephemeral_setting_timestamp: Optional[int] = Field(None, alias="ephemeralSettingTimestamp")

    # Contact/Group info
    is_group: bool = Field(False, alias="isGroup")
    is_read_only: bool = Field(False, alias="isReadOnly")

    # Presence
    presence: Optional[PresenceType] = None

    @property
    def jid(self) -> str:
        """Get the chat JID in the correct format."""
        if "@" not in self.id:
            if self.is_group:
                return f"{self.id}@g.us"
            return f"{self.id}@s.whatsapp.net"
        return self.id

    @property
    def has_unread(self) -> bool:
        """Check if chat has unread messages."""
        return self.unread_count is not None and self.unread_count > 0


class ProfilePicture(BaseModel):
    """Model for profile picture."""

    url: str = Field(..., description="URL of the profile picture")
    id: Optional[str] = Field(None, description="Picture ID")
    type: Optional[str] = Field(None, description="Picture type")
    direct_path: Optional[str] = Field(None, alias="directPath")


class Profile(BaseModel):
    """Model for user profile."""

    name: Optional[str] = Field(None, description="Profile name")
    status: Optional[str] = Field(None, description="Profile status message")
    picture: Optional[ProfilePicture] = Field(None, description="Profile picture")
    about: Optional[str] = Field(None, description="About/Bio")


class PrivacySettings(BaseModel):
    """Model for privacy settings."""

    read_receipts: Optional[PrivacyOption] = Field(None, alias="readreceipts")
    profile: Optional[PrivacyOption] = None
    status: Optional[PrivacyOption] = None
    online: Optional[PrivacyOption] = None
    last: Optional[PrivacyOption] = None
    group_add: Optional[PrivacyOption] = Field(None, alias="groupadd")


class BlockStatus(str, Enum):
    """Block status options."""

    BLOCK = "block"
    UNBLOCK = "unblock"


class WhatsAppNumber(BaseModel):
    """Model for WhatsApp number verification."""

    exists: bool = Field(..., description="Whether the number exists on WhatsApp")
    jid: str = Field(..., description="WhatsApp JID")
    number: str = Field(..., description="Phone number")

    # Business info
    is_business: Optional[bool] = Field(None, alias="isBusiness")
    business: Optional[Dict[str, Any]] = None


class ChatResponse(BaseResponse):
    """Response for chat operations."""

    chat: Optional[Chat] = None
    chats: Optional[List[Chat]] = None
    contact: Optional[Contact] = None
    contacts: Optional[List[Contact]] = None
    numbers: Optional[List[WhatsAppNumber]] = None
    profile: Optional[Profile] = None
    privacy: Optional[PrivacySettings] = None
    profile_pic_url: Optional[str] = Field(None, alias="profilePicUrl")
