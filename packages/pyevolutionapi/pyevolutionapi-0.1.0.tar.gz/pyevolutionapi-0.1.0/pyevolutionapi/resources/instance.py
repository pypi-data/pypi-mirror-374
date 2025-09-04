"""
Instance resource for managing WhatsApp instances.
"""

from typing import Any, Dict, List, Optional

from ..models.instance import Instance, InstanceCreate, InstanceResponse
from .base import BaseResource


class InstanceResource(BaseResource):
    """Resource for managing instances."""

    def create(self, instance_name: str, qrcode: bool = True, **kwargs: Any) -> InstanceResponse:
        """
        Create a new instance.

        Args:
            instance_name: Name of the instance
            qrcode: Whether to return QR code
            **kwargs: Additional instance configuration

        Returns:
            InstanceResponse with created instance details
        """
        data = InstanceCreate(instance_name=instance_name, qrcode=qrcode, **kwargs).dict_for_api()

        response_data = self._post("/instance/create", json=data)
        return self._parse_response(response_data, InstanceResponse)

    def fetch_instances(
        self, instance_name: Optional[str] = None, instance_id: Optional[str] = None
    ) -> List[Instance]:
        """
        Fetch all instances or a specific instance.

        Args:
            instance_name: Optional instance name to filter
            instance_id: Optional instance ID to filter

        Returns:
            List of instances
        """
        params = {}
        if instance_name:
            params["instanceName"] = instance_name
        if instance_id:
            params["instanceId"] = instance_id

        response_data = self._get("/instance/fetchInstances", params=params)

        # Handle response format
        if isinstance(response_data, list):
            return [self._parse_response(item, Instance) for item in response_data]
        elif isinstance(response_data, dict) and "instances" in response_data:
            return [self._parse_response(item, Instance) for item in response_data["instances"]]
        else:
            return []

    def connect(self, instance: str, number: Optional[str] = None) -> InstanceResponse:
        """
        Connect an instance (get QR code or connect with number).

        Args:
            instance: Instance name
            number: Optional phone number to connect directly

        Returns:
            InstanceResponse with QR code or connection status
        """
        params = {}
        if number:
            params["number"] = number

        response_data = self._get(f"/instance/connect/{instance}", params=params)
        return self._parse_response(response_data, InstanceResponse)

    def restart(self, instance: str) -> InstanceResponse:
        """
        Restart an instance.

        Args:
            instance: Instance name

        Returns:
            InstanceResponse with status
        """
        response_data = self._post(f"/instance/restart/{instance}")
        return self._parse_response(response_data, InstanceResponse)

    def connection_state(self, instance: str) -> Dict[str, Any]:
        """
        Get connection state of an instance.

        Args:
            instance: Instance name

        Returns:
            Connection state information
        """
        return self._get(f"/instance/connectionState/{instance}")

    def set_presence(self, instance: str, presence: str = "available") -> Dict[str, Any]:
        """
        Set presence for an instance.

        Args:
            instance: Instance name
            presence: Presence status (available/unavailable)

        Returns:
            Response data
        """
        return self._post(f"/instance/setPresence/{instance}", json={"presence": presence})

    def logout(self, instance: str) -> Dict[str, Any]:
        """
        Logout from an instance.

        Args:
            instance: Instance name

        Returns:
            Response data
        """
        return self._delete(f"/instance/logout/{instance}")

    def delete(self, instance: str) -> Dict[str, Any]:
        """
        Delete an instance.

        Args:
            instance: Instance name

        Returns:
            Response data
        """
        return self._delete(f"/instance/delete/{instance}")

    # Async methods
    async def acreate(
        self, instance_name: str, qrcode: bool = True, **kwargs: Any
    ) -> InstanceResponse:
        """Async version of create."""
        data = InstanceCreate(instance_name=instance_name, qrcode=qrcode, **kwargs).dict_for_api()

        response_data = await self._apost("/instance/create", json=data)
        return self._parse_response(response_data, InstanceResponse)

    async def afetch_instances(
        self, instance_name: Optional[str] = None, instance_id: Optional[str] = None
    ) -> List[Instance]:
        """Async version of fetch_instances."""
        params = {}
        if instance_name:
            params["instanceName"] = instance_name
        if instance_id:
            params["instanceId"] = instance_id

        response_data = await self._aget("/instance/fetchInstances", params=params)

        if isinstance(response_data, list):
            return [self._parse_response(item, Instance) for item in response_data]
        elif isinstance(response_data, dict) and "instances" in response_data:
            return [self._parse_response(item, Instance) for item in response_data["instances"]]
        else:
            return []
