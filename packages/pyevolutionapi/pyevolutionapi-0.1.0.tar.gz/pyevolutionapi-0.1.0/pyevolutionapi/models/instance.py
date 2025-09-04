"""
Models for Instance management.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import BaseModel, BaseResponse, TimestampedModel


class IntegrationType(str, Enum):
    """Available integration types."""

    WHATSAPP_BAILEYS = "WHATSAPP-BAILEYS"
    WHATSAPP_BUSINESS = "WHATSAPP-BUSINESS"
    EVOLUTION = "EVOLUTION"


class ConnectionState(str, Enum):
    """Connection states for an instance."""

    OPEN = "open"
    CLOSE = "close"
    CONNECTING = "connecting"


class InstanceStatus(str, Enum):
    """Status of an instance."""

    CREATED = "created"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    DELETED = "deleted"


class ProxyConfig(BaseModel):
    """Proxy configuration for an instance."""

    enabled: bool = False
    host: Optional[str] = None
    port: Optional[int] = None
    protocol: Optional[str] = "http"
    username: Optional[str] = None
    password: Optional[str] = None


class InstanceSettings(BaseModel):
    """Settings for an instance."""

    reject_call: Optional[bool] = Field(False, alias="rejectCall")
    msg_call: Optional[str] = Field("", alias="msgCall")
    groups_ignore: Optional[bool] = Field(False, alias="groupsIgnore")
    always_online: Optional[bool] = Field(False, alias="alwaysOnline")
    read_messages: Optional[bool] = Field(False, alias="readMessages")
    read_status: Optional[bool] = Field(False, alias="readStatus")
    sync_full_history: Optional[bool] = Field(False, alias="syncFullHistory")


class InstanceCreate(BaseModel):
    """Model for creating a new instance."""

    instance_name: str = Field(..., alias="instanceName", description="Name of the instance")
    token: Optional[str] = Field(None, description="Optional authentication token")
    number: Optional[str] = Field(None, description="WhatsApp number to connect")
    qrcode: Optional[bool] = Field(True, description="Whether to return QR code")
    integration: Optional[IntegrationType] = Field(
        IntegrationType.WHATSAPP_BAILEYS, description="Integration type to use"
    )

    # Settings
    reject_call: Optional[bool] = Field(None, alias="rejectCall")
    msg_call: Optional[str] = Field(None, alias="msgCall")
    groups_ignore: Optional[bool] = Field(None, alias="groupsIgnore")
    always_online: Optional[bool] = Field(None, alias="alwaysOnline")
    read_messages: Optional[bool] = Field(None, alias="readMessages")
    read_status: Optional[bool] = Field(None, alias="readStatus")
    sync_full_history: Optional[bool] = Field(None, alias="syncFullHistory")

    # Proxy settings
    proxy_host: Optional[str] = Field(None, alias="proxyHost")
    proxy_port: Optional[int] = Field(None, alias="proxyPort")
    proxy_protocol: Optional[str] = Field(None, alias="proxyProtocol")
    proxy_username: Optional[str] = Field(None, alias="proxyUsername")
    proxy_password: Optional[str] = Field(None, alias="proxyPassword")

    # Webhook settings
    webhook: Optional[Dict[str, Any]] = None

    # RabbitMQ settings
    rabbitmq: Optional[Dict[str, Any]] = None

    # SQS settings
    sqs: Optional[Dict[str, Any]] = None

    # Chatwoot settings
    chatwoot_account_id: Optional[str] = Field(None, alias="chatwootAccountId")
    chatwoot_token: Optional[str] = Field(None, alias="chatwootToken")
    chatwoot_url: Optional[str] = Field(None, alias="chatwootUrl")
    chatwoot_sign_msg: Optional[bool] = Field(None, alias="chatwootSignMsg")
    chatwoot_reopen_conversation: Optional[bool] = Field(None, alias="chatwootReopenConversation")
    chatwoot_conversation_pending: Optional[bool] = Field(None, alias="chatwootConversationPending")


class Instance(TimestampedModel):
    """Model for an instance."""

    instance_name: str = Field(..., alias="instanceName")
    instance_id: Optional[str] = Field(None, alias="instanceId")
    status: Optional[InstanceStatus] = None
    state: Optional[ConnectionState] = None
    integration: Optional[IntegrationType] = None
    number: Optional[str] = None
    owner: Optional[str] = None
    profile_name: Optional[str] = Field(None, alias="profileName")
    profile_pic_url: Optional[str] = Field(None, alias="profilePicUrl")

    settings: Optional[InstanceSettings] = None
    proxy: Optional[ProxyConfig] = None

    server_url: Optional[str] = Field(None, alias="serverUrl")
    apikey: Optional[str] = None

    # Connection info
    qrcode: Optional[Dict[str, str]] = None  # Contains 'base64' and 'code' fields

    @property
    def is_connected(self) -> bool:
        """Check if instance is connected."""
        return self.state == ConnectionState.OPEN

    @property
    def qr_code_base64(self) -> Optional[str]:
        """Get QR code in base64 format if available."""
        if self.qrcode:
            return self.qrcode.get("base64")
        return None


class InstanceResponse(BaseResponse):
    """Response for instance operations."""

    instance: Optional[Instance] = None
    instances: Optional[List[Instance]] = None
    hash: Optional[str] = Field(None, description="Instance hash/token")
    qrcode: Optional[Dict[str, str]] = None

    # For connection response
    code: Optional[str] = None
    base64: Optional[str] = None

    @property
    def qr_code_base64(self) -> Optional[str]:
        """Get QR code in base64 format."""
        if self.base64:
            return self.base64
        if self.qrcode:
            return self.qrcode.get("base64")
        return None
