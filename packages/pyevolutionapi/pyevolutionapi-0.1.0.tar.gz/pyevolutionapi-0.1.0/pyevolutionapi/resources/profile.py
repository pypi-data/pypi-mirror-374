"""
Profile resource for profile management.
"""

from typing import Any, Dict

from .base import BaseResource


class ProfileResource(BaseResource):
    """Resource for profile management."""

    def fetch_profile(self, instance: str, number: str) -> Dict[str, Any]:
        """
        Fetch profile information.

        Args:
            instance: Instance name
            number: WhatsApp number

        Returns:
            Profile data
        """
        return self._post(f"/chat/fetchProfile/{instance}", json={"number": number})

    def fetch_business_profile(self, instance: str, number: str) -> Dict[str, Any]:
        """
        Fetch business profile information.

        Args:
            instance: Instance name
            number: WhatsApp business number

        Returns:
            Business profile data
        """
        return self._post(f"/chat/fetchBusinessProfile/{instance}", json={"number": number})

    def update_name(self, instance: str, name: str) -> Dict[str, Any]:
        """
        Update profile name.

        Args:
            instance: Instance name
            name: New profile name

        Returns:
            Response data
        """
        return self._post(f"/chat/updateProfileName/{instance}", json={"name": name})

    def update_status(self, instance: str, status: str) -> Dict[str, Any]:
        """
        Update profile status message.

        Args:
            instance: Instance name
            status: New status message

        Returns:
            Response data
        """
        return self._post(f"/chat/updateProfileStatus/{instance}", json={"status": status})

    def update_picture(self, instance: str, picture: str) -> Dict[str, Any]:
        """
        Update profile picture.

        Args:
            instance: Instance name
            picture: Picture URL or base64

        Returns:
            Response data
        """
        return self._post(f"/chat/updateProfilePicture/{instance}", json={"picture": picture})

    def remove_picture(self, instance: str) -> Dict[str, Any]:
        """
        Remove profile picture.

        Args:
            instance: Instance name

        Returns:
            Response data
        """
        return self._delete(f"/chat/removeProfilePicture/{instance}")

    def fetch_privacy_settings(self, instance: str) -> Dict[str, Any]:
        """
        Fetch privacy settings.

        Args:
            instance: Instance name

        Returns:
            Privacy settings data
        """
        return self._get(f"/chat/fetchPrivacySettings/{instance}")

    def update_privacy_settings(self, instance: str, settings: Dict[str, str]) -> Dict[str, Any]:
        """
        Update privacy settings.

        Args:
            instance: Instance name
            settings: Privacy settings dictionary

        Returns:
            Response data
        """
        return self._post(f"/chat/updatePrivacySettings/{instance}", json=settings)
