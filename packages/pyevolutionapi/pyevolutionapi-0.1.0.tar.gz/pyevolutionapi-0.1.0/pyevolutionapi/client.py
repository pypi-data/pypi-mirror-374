"""
Main client for Evolution API.
"""

import os
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import httpx
from dotenv import load_dotenv

from .auth import ApiKeyAuth, AuthHandler
from .exceptions import (
    AuthenticationError,
    EvolutionAPIError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from .exceptions import ConnectionError as EvolutionConnectionError
from .exceptions import TimeoutError as EvolutionTimeoutError
from .resources import (
    ChatResource,
    GroupResource,
    InstanceResource,
    MessageResource,
    ProfileResource,
    WebhookResource,
)

# Load environment variables
load_dotenv()


class EvolutionClient:
    """
    Main client for interacting with Evolution API.

    Example:
        >>> client = EvolutionClient("http://localhost:8080", api_key="your-key")
        >>> instance = client.instance.create(instance_name="my-instance")
        >>> client.messages.send_text(instance="my-instance", number="5511999999999", text="Hello!")
    """

    DEFAULT_TIMEOUT = 30.0
    DEFAULT_MAX_RETRIES = 3

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        default_instance: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        verify_ssl: bool = True,
        debug: bool = False,
        **kwargs: Any,
    ):
        """
        Initialize Evolution API client.

        Args:
            base_url: Base URL of the Evolution API
            api_key: Global API key for authentication
            default_instance: Default instance name to use
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            verify_ssl: Whether to verify SSL certificates
            debug: Enable debug mode
            **kwargs: Additional configuration options
        """
        # Get configuration from environment if not provided
        self.base_url = (
            base_url or os.getenv("EVOLUTION_BASE_URL", "http://localhost:8080")
        ).rstrip("/")
        self.api_key = api_key or os.getenv("EVOLUTION_API_KEY")
        self.default_instance = default_instance or os.getenv("EVOLUTION_INSTANCE_NAME")

        # Request configuration
        self.timeout = timeout or float(
            os.getenv("EVOLUTION_REQUEST_TIMEOUT", str(self.DEFAULT_TIMEOUT))
        )
        self.max_retries = max_retries or int(
            os.getenv("EVOLUTION_MAX_RETRIES", str(self.DEFAULT_MAX_RETRIES))
        )
        self.verify_ssl = verify_ssl
        self.debug = debug or os.getenv("EVOLUTION_DEBUG", "").lower() in ["true", "1", "yes"]

        # Initialize auth handler
        self.auth = AuthHandler(api_key=self.api_key)

        # Configure HTTP client
        self._configure_client()

        # Initialize resources
        self._init_resources()

    def _configure_client(self) -> None:
        """Configure the HTTP client."""
        # Set up auth
        auth = None
        if self.api_key:
            auth = ApiKeyAuth(self.api_key)

        # Configure transport with retries
        transport = httpx.HTTPTransport(
            retries=self.max_retries,
            verify=self.verify_ssl,
        )

        # Create client
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            transport=transport,
            auth=auth,
            headers={
                "User-Agent": "PyEvolution/0.1.0",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

        # Create async client
        self._async_client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            transport=httpx.AsyncHTTPTransport(retries=self.max_retries),
            auth=auth,
            headers={
                "User-Agent": "PyEvolution/0.1.0",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

    def _init_resources(self) -> None:
        """Initialize API resources."""
        self.instance = InstanceResource(self)
        self.instances = self.instance  # Alias

        self.messages = MessageResource(self)
        self.message = self.messages  # Alias

        self.chat = ChatResource(self)
        self.chats = self.chat  # Alias

        self.group = GroupResource(self)
        self.groups = self.group  # Alias

        self.profile = ProfileResource(self)

        self.webhook = WebhookResource(self)
        self.webhooks = self.webhook  # Alias

    def request(
        self,
        method: str,
        endpoint: str,
        instance: Optional[str] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Make an HTTP request to the Evolution API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (will be joined with base_url)
            instance: Instance name (uses default if not provided)
            json: JSON data to send
            data: Form data to send
            params: Query parameters
            headers: Additional headers
            files: Files to upload
            **kwargs: Additional request parameters

        Returns:
            httpx.Response object

        Raises:
            EvolutionAPIError: For API errors
            AuthenticationError: For auth errors
            NotFoundError: For 404 errors
            ValidationError: For validation errors
            RateLimitError: For rate limit errors
        """
        # Use instance from parameter or default
        if instance is None:
            instance = self.default_instance

        # Replace instance placeholder in endpoint if present
        if instance and "{instance}" in endpoint:
            endpoint = endpoint.replace("{instance}", instance)

        # Build full URL
        url = urljoin(self.base_url, endpoint.lstrip("/"))

        # Prepare request
        request_kwargs = {
            "method": method,
            "url": url,
            "params": params,
            "headers": headers or {},
        }

        if json is not None:
            request_kwargs["json"] = json
        elif data is not None:
            request_kwargs["data"] = data
        elif files is not None:
            request_kwargs["files"] = files

        # Add any additional kwargs
        request_kwargs.update(kwargs)

        # Make request
        try:
            if self.debug:
                print(f"[DEBUG] {method} {url}")
                if json:
                    print(f"[DEBUG] Body: {json}")

            response = self._client.request(**request_kwargs)

            if self.debug:
                print(f"[DEBUG] Response: {response.status_code}")

        except httpx.TimeoutException as e:
            raise EvolutionTimeoutError(f"Request timed out: {e}") from e
        except httpx.ConnectError as e:
            raise EvolutionConnectionError(f"Connection failed: {e}") from e
        except Exception as e:
            raise EvolutionAPIError(f"Request failed: {e}") from e

        # Handle response
        self._handle_response(response)
        return response

    async def arequest(
        self, method: str, endpoint: str, instance: Optional[str] = None, **kwargs
    ) -> httpx.Response:
        """
        Make an async HTTP request to the Evolution API.

        See `request` method for parameters.
        """
        # Use instance from parameter or default
        if instance is None:
            instance = self.default_instance

        # Replace instance placeholder in endpoint if present
        if instance and "{instance}" in endpoint:
            endpoint = endpoint.replace("{instance}", instance)

        # Build full URL
        url = urljoin(self.base_url, endpoint.lstrip("/"))

        # Prepare request
        request_kwargs = {"method": method, "url": url, **kwargs}

        # Make request
        try:
            response = await self._async_client.request(**request_kwargs)
        except httpx.TimeoutException as e:
            raise EvolutionTimeoutError(f"Request timed out: {e}") from e
        except httpx.ConnectError as e:
            raise EvolutionConnectionError(f"Connection failed: {e}") from e
        except Exception as e:
            raise EvolutionAPIError(f"Request failed: {e}") from e

        # Handle response
        self._handle_response(response)
        return response

    def _handle_response(self, response: httpx.Response) -> None:
        """
        Handle API response and raise appropriate exceptions for errors.

        Args:
            response: The httpx Response object

        Raises:
            Various EvolutionAPIError subclasses based on status code
        """
        if response.is_success:
            return

        # Try to get error message from response
        try:
            error_data = response.json()
            message = error_data.get("message", error_data.get("error", str(response.text)))
        except Exception:
            message = response.text or f"HTTP {response.status_code}"
            error_data = {}

        # Handle specific status codes
        if response.status_code == 401:
            raise AuthenticationError(message, status_code=401, response_data=error_data)
        elif response.status_code == 404:
            raise NotFoundError(message, status_code=404, response_data=error_data)
        elif response.status_code == 400:
            raise ValidationError(message, status_code=400, response_data=error_data)
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                message,
                status_code=429,
                response_data=error_data,
                retry_after=int(retry_after) if retry_after else None,
            )
        elif response.status_code >= 500:
            raise EvolutionAPIError(
                f"Server error: {message}",
                status_code=response.status_code,
                response_data=error_data,
            )
        else:
            raise EvolutionAPIError(
                message, status_code=response.status_code, response_data=error_data
            )

    def close(self) -> None:
        """Close the HTTP client connections."""
        self._client.close()

    async def aclose(self) -> None:
        """Close the async HTTP client connections."""
        await self._async_client.aclose()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.aclose()

    def set_default_instance(self, instance_name: str) -> None:
        """
        Set the default instance to use for all operations.

        Args:
            instance_name: Name of the instance
        """
        self.default_instance = instance_name

    def health_check(self) -> bool:
        """
        Check if the API is healthy and reachable.

        Returns:
            True if API is healthy, False otherwise
        """
        try:
            response = self._client.get("/")
            return response.is_success
        except Exception:
            return False

    async def ahealth_check(self) -> bool:
        """
        Async check if the API is healthy and reachable.

        Returns:
            True if API is healthy, False otherwise
        """
        try:
            response = await self._async_client.get("/")
            return response.is_success
        except Exception:
            return False
