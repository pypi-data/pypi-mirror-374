"""
Authentication module for Evolution API.
"""

from typing import Dict, Optional

import httpx

from .exceptions import AuthenticationError


class AuthHandler:
    """Handles authentication for Evolution API requests."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize authentication handler.

        Args:
            api_key: Global API key for authentication
        """
        self.api_key = api_key
        self._instance_tokens: Dict[str, str] = {}

    def set_api_key(self, api_key: str) -> None:
        """Set or update the global API key."""
        self.api_key = api_key

    def set_instance_token(self, instance_name: str, token: str) -> None:
        """
        Set authentication token for a specific instance.

        Args:
            instance_name: Name of the instance
            token: Authentication token for the instance
        """
        self._instance_tokens[instance_name] = token

    def get_instance_token(self, instance_name: str) -> Optional[str]:
        """
        Get authentication token for a specific instance.

        Args:
            instance_name: Name of the instance

        Returns:
            Token if exists, None otherwise
        """
        return self._instance_tokens.get(instance_name)

    def clear_instance_token(self, instance_name: str) -> None:
        """Remove authentication token for a specific instance."""
        self._instance_tokens.pop(instance_name, None)

    def get_headers(self, instance_name: Optional[str] = None) -> Dict[str, str]:
        """
        Get authentication headers for a request.

        Args:
            instance_name: Optional instance name for instance-specific auth

        Returns:
            Dictionary with authentication headers

        Raises:
            AuthenticationError: If no authentication method is available
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Check for instance-specific token first
        if instance_name and instance_name in self._instance_tokens:
            headers["apikey"] = self._instance_tokens[instance_name]
            return headers

        # Fall back to global API key
        if self.api_key:
            headers["apikey"] = self.api_key
            return headers

        # No authentication available
        raise AuthenticationError(
            "No authentication method available. " "Please provide an API key or instance token."
        )

    def apply_auth(self, request: httpx.Request, instance_name: Optional[str] = None) -> None:
        """
        Apply authentication to an HTTP request.

        Args:
            request: The httpx.Request object to modify
            instance_name: Optional instance name for instance-specific auth
        """
        headers = self.get_headers(instance_name)
        request.headers.update(headers)

    def is_authenticated(self, instance_name: Optional[str] = None) -> bool:
        """
        Check if authentication is available.

        Args:
            instance_name: Optional instance name to check

        Returns:
            True if authentication is available, False otherwise
        """
        if instance_name and instance_name in self._instance_tokens:
            return True
        return self.api_key is not None


class BearerAuth(httpx.Auth):
    """Bearer token authentication for httpx."""

    def __init__(self, token: str):
        self.token = token

    def auth_flow(self, request: httpx.Request):
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request


class ApiKeyAuth(httpx.Auth):
    """API key authentication for httpx."""

    def __init__(self, api_key: str, header_name: str = "apikey"):
        self.api_key = api_key
        self.header_name = header_name

    def auth_flow(self, request: httpx.Request):
        request.headers[self.header_name] = self.api_key
        yield request
