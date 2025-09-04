"""
Models for Message operations.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import Field, HttpUrl

from .base import BaseModel, BaseResponse


class MessageStatus(str, Enum):
    """Message status types."""

    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    READ = "READ"
    FAILED = "FAILED"


class MediaType(str, Enum):
    """Media types for messages."""

    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"


class MessageType(str, Enum):
    """Types of messages."""

    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    LOCATION = "location"
    CONTACT = "contact"
    STICKER = "sticker"
    POLL = "poll"
    LIST = "list"
    BUTTONS = "buttons"
    REACTION = "reaction"


class BaseMessage(BaseModel):
    """Base model for all message types."""

    number: str = Field(..., description="Recipient phone number (without @s.whatsapp.net)")
    delay: Optional[int] = Field(None, description="Delay in milliseconds before sending")
    quoted: Optional[Dict[str, Any]] = Field(None, description="Message to quote/reply to")
    mentions_everyone: Optional[bool] = Field(None, alias="mentionsEveryOne")
    mentioned: Optional[List[str]] = Field(None, description="Numbers to mention")


class TextMessage(BaseMessage):
    """Model for sending text messages."""

    text: str = Field(..., description="Text content to send")
    link_preview: Optional[bool] = Field(True, alias="linkPreview")


class MediaMessage(BaseMessage):
    """Model for sending media messages."""

    mediatype: MediaType = Field(..., description="Type of media")
    media: Union[str, HttpUrl] = Field(..., description="URL or base64 of the media")
    caption: Optional[str] = Field(None, description="Caption for the media")
    mimetype: Optional[str] = Field(None, description="MIME type of the media")
    file_name: Optional[str] = Field(None, alias="fileName", description="File name for documents")


class AudioMessage(BaseMessage):
    """Model for sending audio messages."""

    audio: Union[str, HttpUrl] = Field(..., description="URL or base64 of the audio")
    encoding: Optional[bool] = Field(True, description="Whether to encode as WhatsApp audio")


class LocationMessage(BaseMessage):
    """Model for sending location messages."""

    name: str = Field(..., description="Name of the location")
    address: str = Field(..., description="Address of the location")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")


class ContactCard(BaseModel):
    """Model for a contact card."""

    full_name: str = Field(..., alias="fullName")
    wuid: str = Field(..., description="WhatsApp user ID (phone without formatting)")
    phone_number: Optional[str] = Field(None, alias="phoneNumber")
    organization: Optional[str] = None
    email: Optional[str] = None
    url: Optional[str] = None


class ContactMessage(BaseMessage):
    """Model for sending contact messages."""

    contact: List[ContactCard] = Field(..., description="List of contacts to send")


class ReactionMessage(BaseModel):
    """Model for sending reaction to messages."""

    key: Dict[str, Any] = Field(..., description="Message key to react to")
    reaction: str = Field(..., description="Emoji reaction")


class PollMessage(BaseMessage):
    """Model for sending poll messages."""

    name: str = Field(..., description="Poll question")
    selectable_count: int = Field(
        1, alias="selectableCount", description="How many options can be selected"
    )
    values: List[str] = Field(..., description="Poll options")


class ListRow(BaseModel):
    """Model for a list row."""

    title: str
    description: str
    row_id: str = Field(..., alias="rowId")


class ListSection(BaseModel):
    """Model for a list section."""

    title: str
    rows: List[ListRow]


class ListMessage(BaseMessage):
    """Model for sending list messages."""

    title: str
    description: str
    button_text: str = Field(..., alias="buttonText")
    footer_text: Optional[str] = Field(None, alias="footerText")
    sections: List[ListSection]


class Button(BaseModel):
    """Model for a button."""

    type: str  # reply, copy, url, call, pix
    display_text: str = Field(..., alias="displayText")
    id: Optional[str] = None
    copy_code: Optional[str] = Field(None, alias="copyCode")
    url: Optional[str] = None
    phone_number: Optional[str] = Field(None, alias="phoneNumber")


class ButtonMessage(BaseMessage):
    """Model for sending button messages."""

    title: str
    description: str
    footer: Optional[str] = None
    buttons: List[Button]


class StickerMessage(BaseMessage):
    """Model for sending sticker messages."""

    sticker: Union[str, HttpUrl] = Field(..., description="URL or base64 of the sticker")


class StatusMessage(BaseModel):
    """Model for sending status/stories."""

    type: MessageType = Field(..., description="Type of status (text, image, video, audio)")
    content: str = Field(..., description="Content (text or URL)")
    caption: Optional[str] = Field(None, description="Caption for media status")
    background_color: Optional[str] = Field(None, alias="backgroundColor")
    font: Optional[int] = Field(None, description="Font style for text status (1-5)")
    all_contacts: bool = Field(False, alias="allContacts")
    status_jid_list: Optional[List[str]] = Field(None, alias="statusJidList")


class MessageKey(BaseModel):
    """Model for message key/identifier."""

    remote_jid: str = Field(..., alias="remoteJid")
    from_me: bool = Field(..., alias="fromMe")
    id: str


class MessageInfo(BaseModel):
    """Model for message information."""

    key: MessageKey
    message: Optional[Dict[str, Any]] = None
    message_timestamp: Optional[int] = Field(None, alias="messageTimestamp")
    status: Optional[MessageStatus] = None
    participant: Optional[str] = None


class MessageResponse(BaseResponse):
    """Response for message operations."""

    key: Optional[MessageKey] = None
    message: Optional[MessageInfo] = None
    messages: Optional[List[MessageInfo]] = None

    @property
    def message_id(self) -> Optional[str]:
        """Get the message ID if available."""
        if self.key:
            return self.key.id
        if self.message and self.message.key:
            return self.message.key.id
        return None
