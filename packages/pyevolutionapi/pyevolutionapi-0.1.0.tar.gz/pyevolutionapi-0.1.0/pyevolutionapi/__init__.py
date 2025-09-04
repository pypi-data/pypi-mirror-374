"""
PyEvolution - Python client for Evolution API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A modern, type-safe Python client for Evolution API - WhatsApp integration made simple.

Basic usage:
    >>> from pyevolution import EvolutionClient
    >>> client = EvolutionClient(base_url="http://localhost:8080", api_key="your-key")
    >>> instance = client.instance.create(name="my-instance")
    >>> client.messages.send_text(instance="my-instance", number="5511999999999", text="Hello!")

Full documentation is available at https://github.com/lpcoutinho/pyevolution
"""

from typing import Optional

__version__ = "0.1.0"
__author__ = "Luiz Paulo Coutinho"
__email__ = "your.email@example.com"
__license__ = "MIT"

from .client import EvolutionClient
from .exceptions import (
    AuthenticationError,
    ConnectionError,
    EvolutionAPIError,
    NotFoundError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)

__all__ = [
    "EvolutionClient",
    "EvolutionAPIError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "ConnectionError",
    "TimeoutError",
    "RateLimitError",
]


def create_client(
    base_url: str, api_key: Optional[str] = None, instance_name: Optional[str] = None, **kwargs
) -> EvolutionClient:
    """
    Factory function to create an Evolution API client.

    Args:
        base_url: The base URL of the Evolution API
        api_key: Global API key for authentication (optional)
        instance_name: Default instance name to use (optional)
        **kwargs: Additional configuration options

    Returns:
        EvolutionClient: Configured client instance

    Example:
        >>> client = create_client("http://localhost:8080", api_key="my-key")
    """
    return EvolutionClient(
        base_url=base_url, api_key=api_key, default_instance=instance_name, **kwargs
    )
