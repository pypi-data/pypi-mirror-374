"""
Base resource class for API resources.
"""

from typing import TYPE_CHECKING, Any, Dict, Optional, Type, TypeVar

from pydantic import BaseModel

if TYPE_CHECKING:
    from ..client import EvolutionClient

T = TypeVar("T", bound=BaseModel)


class BaseResource:
    """Base class for all API resources."""

    def __init__(self, client: "EvolutionClient"):
        """
        Initialize resource with client.

        Args:
            client: The Evolution API client instance
        """
        self.client = client

    def _get(
        self,
        endpoint: str,
        instance: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a GET request."""
        response = self.client.request("GET", endpoint, instance=instance, params=params, **kwargs)
        return response.json()

    def _post(
        self,
        endpoint: str,
        instance: Optional[str] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a POST request."""
        response = self.client.request(
            "POST", endpoint, instance=instance, json=json, data=data, files=files, **kwargs
        )
        return response.json()

    def _put(
        self,
        endpoint: str,
        instance: Optional[str] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a PUT request."""
        response = self.client.request("PUT", endpoint, instance=instance, json=json, **kwargs)
        return response.json()

    def _delete(
        self,
        endpoint: str,
        instance: Optional[str] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a DELETE request."""
        response = self.client.request("DELETE", endpoint, instance=instance, json=json, **kwargs)
        if response.text:
            return response.json()
        return {"status": "success"}

    def _parse_response(self, response_data: Dict[str, Any], model: Type[T]) -> T:
        """
        Parse response data into a Pydantic model.

        Args:
            response_data: The response data dictionary
            model: The Pydantic model class to parse into

        Returns:
            Instance of the model
        """
        return model.model_validate(response_data)

    async def _aget(
        self,
        endpoint: str,
        instance: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make an async GET request."""
        response = await self.client.arequest(
            "GET", endpoint, instance=instance, params=params, **kwargs
        )
        return response.json()

    async def _apost(
        self,
        endpoint: str,
        instance: Optional[str] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make an async POST request."""
        response = await self.client.arequest(
            "POST", endpoint, instance=instance, json=json, data=data, files=files, **kwargs
        )
        return response.json()

    async def _aput(
        self,
        endpoint: str,
        instance: Optional[str] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make an async PUT request."""
        response = await self.client.arequest(
            "PUT", endpoint, instance=instance, json=json, **kwargs
        )
        return response.json()

    async def _adelete(
        self,
        endpoint: str,
        instance: Optional[str] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make an async DELETE request."""
        response = await self.client.arequest(
            "DELETE", endpoint, instance=instance, json=json, **kwargs
        )
        if response.text:
            return response.json()
        return {"status": "success"}
