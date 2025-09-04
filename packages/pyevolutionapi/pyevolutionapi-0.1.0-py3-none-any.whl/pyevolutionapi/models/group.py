"""
Models for Group management.
"""

from enum import Enum
from typing import List, Optional

from pydantic import Field

from .base import BaseModel, BaseResponse, TimestampedModel


class ParticipantRole(str, Enum):
    """Roles for group participants."""

    ADMIN = "admin"
    MEMBER = "member"
    SUPERADMIN = "superadmin"


class GroupAction(str, Enum):
    """Actions for group management."""

    ADD = "add"
    REMOVE = "remove"
    PROMOTE = "promote"
    DEMOTE = "demote"


class GroupSetting(str, Enum):
    """Group settings."""

    ANNOUNCEMENT = "announcement"
    NOT_ANNOUNCEMENT = "not_announcement"
    LOCKED = "locked"
    UNLOCKED = "unlocked"


class GroupParticipant(BaseModel):
    """Model for a group participant."""

    id: str = Field(..., description="WhatsApp ID of the participant")
    admin: Optional[ParticipantRole] = None
    is_admin: Optional[bool] = Field(None, alias="isAdmin")
    is_super_admin: Optional[bool] = Field(None, alias="isSuperAdmin")

    # Profile info
    name: Optional[str] = None
    notify: Optional[str] = None
    profile_pic_url: Optional[str] = Field(None, alias="profilePicUrl")

    @property
    def role(self) -> ParticipantRole:
        """Get participant role."""
        if self.is_super_admin:
            return ParticipantRole.SUPERADMIN
        if self.is_admin or self.admin == ParticipantRole.ADMIN:
            return ParticipantRole.ADMIN
        return ParticipantRole.MEMBER


class GroupCreate(BaseModel):
    """Model for creating a group."""

    subject: str = Field(..., description="Group name/subject")
    description: Optional[str] = Field(None, description="Group description")
    participants: List[str] = Field(..., description="List of phone numbers to add")


class GroupUpdate(BaseModel):
    """Model for updating group information."""

    subject: Optional[str] = Field(None, description="New group subject")
    description: Optional[str] = Field(None, description="New group description")
    image: Optional[str] = Field(None, description="Group picture URL or base64")


class GroupInvite(BaseModel):
    """Model for group invite information."""

    code: str = Field(..., description="Invite code")
    expiration: Optional[int] = Field(None, description="Expiration timestamp")
    group_jid: Optional[str] = Field(None, alias="groupJid")
    invite_link: Optional[str] = Field(None, alias="inviteLink")

    @property
    def link(self) -> str:
        """Get the full invite link."""
        if self.invite_link:
            return self.invite_link
        return f"https://chat.whatsapp.com/{self.code}"


class Group(TimestampedModel):
    """Model for a group."""

    id: str = Field(..., description="Group JID")
    subject: str = Field(..., description="Group name/subject")
    subject_owner: Optional[str] = Field(None, alias="subjectOwner")
    subject_time: Optional[int] = Field(None, alias="subjectTime")

    description: Optional[str] = None
    desc_id: Optional[str] = Field(None, alias="descId")
    desc_owner: Optional[str] = Field(None, alias="descOwner")
    desc_time: Optional[int] = Field(None, alias="descTime")

    creation: Optional[int] = Field(None, description="Group creation timestamp")
    owner: Optional[str] = Field(None, description="Group owner JID")

    participants: Optional[List[GroupParticipant]] = None
    size: Optional[int] = Field(None, description="Number of participants")

    announce: Optional[bool] = Field(None, description="Only admins can send messages")
    restrict: Optional[bool] = Field(None, description="Only admins can edit group info")

    ephemeral_duration: Optional[int] = Field(None, alias="ephemeralDuration")

    # Group picture
    profile_pic_url: Optional[str] = Field(None, alias="profilePicUrl")

    # Invite info
    invite_code: Optional[str] = Field(None, alias="inviteCode")

    @property
    def group_jid(self) -> str:
        """Get the group JID in the correct format."""
        if "@" not in self.id:
            return f"{self.id}@g.us"
        return self.id

    @property
    def is_admin(self, participant_id: str) -> bool:
        """Check if a participant is an admin."""
        if self.participants:
            for p in self.participants:
                if p.id == participant_id:
                    return p.role in [ParticipantRole.ADMIN, ParticipantRole.SUPERADMIN]
        return False


class ParticipantUpdate(BaseModel):
    """Model for updating group participants."""

    action: GroupAction = Field(..., description="Action to perform")
    participants: List[str] = Field(..., description="List of phone numbers")


class GroupSettingUpdate(BaseModel):
    """Model for updating group settings."""

    action: GroupSetting = Field(..., description="Setting to apply")


class GroupResponse(BaseResponse):
    """Response for group operations."""

    group: Optional[Group] = None
    groups: Optional[List[Group]] = None
    participants: Optional[List[GroupParticipant]] = None
    invite_code: Optional[str] = Field(None, alias="inviteCode")
    invite_link: Optional[str] = Field(None, alias="inviteLink")

    @property
    def group_jid(self) -> Optional[str]:
        """Get the group JID if available."""
        if self.group:
            return self.group.group_jid
        return None
