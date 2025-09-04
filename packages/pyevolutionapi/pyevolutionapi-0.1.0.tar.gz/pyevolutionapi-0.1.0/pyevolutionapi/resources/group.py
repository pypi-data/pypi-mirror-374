"""
Group resource for group management.
"""

from typing import Any, Dict, List, Optional

from ..models.group import Group, GroupCreate, GroupResponse
from .base import BaseResource


class GroupResource(BaseResource):
    """Resource for group management."""

    def create(
        self,
        instance: str,
        subject: str,
        description: Optional[str] = None,
        participants: List[str] = None,
    ) -> GroupResponse:
        """
        Create a new group.

        Args:
            instance: Instance name
            subject: Group name/subject
            description: Optional group description
            participants: List of phone numbers to add

        Returns:
            GroupResponse with created group details
        """
        group_data = GroupCreate(
            subject=subject, description=description, participants=participants or []
        )
        response_data = self._post(f"/group/create/{instance}", json=group_data.dict_for_api())
        return self._parse_response(response_data, GroupResponse)

    def update_picture(self, instance: str, group_jid: str, image: str) -> Dict[str, Any]:
        """
        Update group picture.

        Args:
            instance: Instance name
            group_jid: Group JID
            image: Image URL or base64

        Returns:
            Response data
        """
        return self._post(
            f"/group/updateGroupPicture/{instance}",
            params={"groupJid": group_jid},
            json={"image": image},
        )

    def update_subject(self, instance: str, group_jid: str, subject: str) -> Dict[str, Any]:
        """
        Update group subject/name.

        Args:
            instance: Instance name
            group_jid: Group JID
            subject: New group subject

        Returns:
            Response data
        """
        return self._post(
            f"/group/updateGroupSubject/{instance}",
            params={"groupJid": group_jid},
            json={"subject": subject},
        )

    def update_description(self, instance: str, group_jid: str, description: str) -> Dict[str, Any]:
        """
        Update group description.

        Args:
            instance: Instance name
            group_jid: Group JID
            description: New group description

        Returns:
            Response data
        """
        return self._post(
            f"/group/updateGroupDescription/{instance}",
            params={"groupJid": group_jid},
            json={"description": description},
        )

    def get_invite_code(self, instance: str, group_jid: str) -> Dict[str, Any]:
        """
        Get group invite code.

        Args:
            instance: Instance name
            group_jid: Group JID

        Returns:
            Invite code data
        """
        return self._get(f"/group/inviteCode/{instance}", params={"groupJid": group_jid})

    def revoke_invite_code(self, instance: str, group_jid: str) -> Dict[str, Any]:
        """
        Revoke group invite code.

        Args:
            instance: Instance name
            group_jid: Group JID

        Returns:
            Response data
        """
        return self._post(f"/group/revokeInviteCode/{instance}", params={"groupJid": group_jid})

    def update_participant(
        self, instance: str, group_jid: str, action: str, participants: List[str]
    ) -> Dict[str, Any]:
        """
        Update group participants (add, remove, promote, demote).

        Args:
            instance: Instance name
            group_jid: Group JID
            action: Action to perform (add, remove, promote, demote)
            participants: List of participant numbers

        Returns:
            Response data
        """
        return self._post(
            f"/group/updateParticipant/{instance}",
            params={"groupJid": group_jid},
            json={"action": action, "participants": participants},
        )

    def fetch_all_groups(self, instance: str, get_participants: bool = False) -> List[Group]:
        """
        Fetch all groups.

        Args:
            instance: Instance name
            get_participants: Whether to include participant details

        Returns:
            List of groups
        """
        response_data = self._get(
            f"/group/fetchAllGroups/{instance}",
            params={"getParticipants": str(get_participants).lower()},
        )

        if isinstance(response_data, list):
            return [self._parse_response(item, Group) for item in response_data]
        return []

    def get_participants(self, instance: str, group_jid: str) -> Dict[str, Any]:
        """
        Get group participants.

        Args:
            instance: Instance name
            group_jid: Group JID

        Returns:
            Participants data
        """
        return self._get(f"/group/participants/{instance}", params={"groupJid": group_jid})

    def leave_group(self, instance: str, group_jid: str) -> Dict[str, Any]:
        """
        Leave a group.

        Args:
            instance: Instance name
            group_jid: Group JID

        Returns:
            Response data
        """
        return self._delete(f"/group/leaveGroup/{instance}", params={"groupJid": group_jid})
