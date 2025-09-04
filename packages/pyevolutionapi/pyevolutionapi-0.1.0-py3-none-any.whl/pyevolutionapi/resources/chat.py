"""
Chat resource for chat operations.
"""

from typing import Any, Dict, List, Optional

from ..models.chat import Chat, Contact
from .base import BaseResource


class ChatResource(BaseResource):
    """Resource for chat operations."""

    def whatsapp_numbers(self, instance: str, numbers: List[str]) -> List[Dict[str, Any]]:
        """
        Check if numbers exist on WhatsApp.

        Args:
            instance: Instance name
            numbers: List of phone numbers to check

        Returns:
            List of number verification results
        """
        return self._post(f"/chat/whatsappNumbers/{instance}", json={"numbers": numbers})

    def mark_as_read(self, instance: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Mark messages as read.

        Args:
            instance: Instance name
            messages: List of message keys to mark as read

        Returns:
            Response data
        """
        return self._post(f"/chat/markMessageAsRead/{instance}", json={"readMessages": messages})

    def fetch_profile_picture(self, instance: str, number: str) -> Dict[str, Any]:
        """
        Fetch profile picture URL.

        Args:
            instance: Instance name
            number: WhatsApp number

        Returns:
            Profile picture data
        """
        return self._post(f"/chat/fetchProfilePictureUrl/{instance}", json={"number": number})

    def find_contacts(self, instance: str, where: Optional[Dict[str, Any]] = None) -> List[Contact]:
        """
        Find contacts.

        Args:
            instance: Instance name
            where: Optional filter criteria

        Returns:
            List of contacts
        """
        response_data = self._post(f"/chat/findContacts/{instance}", json={"where": where or {}})

        if isinstance(response_data, list):
            return [self._parse_response(item, Contact) for item in response_data]
        return []

    def find_messages(
        self, instance: str, where: Optional[Dict[str, Any]] = None, page: int = 1, offset: int = 10
    ) -> Dict[str, Any]:
        """
        Find messages.

        Args:
            instance: Instance name
            where: Filter criteria
            page: Page number
            offset: Messages per page

        Returns:
            Messages data
        """
        return self._post(
            f"/chat/findMessages/{instance}",
            json={"where": where or {}, "page": page, "offset": offset},
        )

    def find_chats(self, instance: str) -> List[Chat]:
        """
        Find all chats.

        Args:
            instance: Instance name

        Returns:
            List of chats
        """
        response_data = self._post(f"/chat/findChats/{instance}")

        if isinstance(response_data, list):
            return [self._parse_response(item, Chat) for item in response_data]
        return []

    def send_presence(
        self, instance: str, number: str, presence: str = "composing", delay: int = 1200
    ) -> Dict[str, Any]:
        """
        Send presence/typing indicator.

        Args:
            instance: Instance name
            number: Recipient number
            presence: Presence type (composing, recording, etc.)
            delay: Duration in milliseconds

        Returns:
            Response data
        """
        return self._post(
            f"/chat/sendPresence/{instance}",
            json={"number": number, "presence": presence, "delay": delay},
        )

    def update_block_status(
        self, instance: str, number: str, status: str = "block"
    ) -> Dict[str, Any]:
        """
        Block or unblock a contact.

        Args:
            instance: Instance name
            number: Contact number
            status: "block" or "unblock"

        Returns:
            Response data
        """
        return self._post(
            f"/message/updateBlockStatus/{instance}", json={"number": number, "status": status}
        )
