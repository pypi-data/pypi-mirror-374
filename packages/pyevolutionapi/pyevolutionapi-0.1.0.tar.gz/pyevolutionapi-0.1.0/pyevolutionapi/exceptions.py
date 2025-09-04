"""
Custom exceptions for PyEvolution.
"""

from typing import Any, Dict, Optional


class EvolutionAPIError(Exception):
    """Base exception for all Evolution API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        request_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        self.request_data = request_data or {}

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(EvolutionAPIError):
    """Raised when authentication fails."""

    pass


class NotFoundError(EvolutionAPIError):
    """Raised when a resource is not found."""

    pass


class ValidationError(EvolutionAPIError):
    """Raised when request validation fails."""

    def __init__(self, message: str, errors: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.errors = errors or {}


class ConnectionError(EvolutionAPIError):
    """Raised when connection to the API fails."""

    pass


class TimeoutError(EvolutionAPIError):
    """Raised when a request times out."""

    pass


class RateLimitError(EvolutionAPIError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class WebhookError(EvolutionAPIError):
    """Raised when webhook configuration fails."""

    pass


class InstanceError(EvolutionAPIError):
    """Raised when instance operations fail."""

    pass


class MessageError(EvolutionAPIError):
    """Raised when message sending fails."""

    pass


class MediaError(MessageError):
    """Raised when media operations fail."""

    pass


class GroupError(EvolutionAPIError):
    """Raised when group operations fail."""

    pass


class IntegrationError(EvolutionAPIError):
    """Raised when integration configuration fails."""

    pass
