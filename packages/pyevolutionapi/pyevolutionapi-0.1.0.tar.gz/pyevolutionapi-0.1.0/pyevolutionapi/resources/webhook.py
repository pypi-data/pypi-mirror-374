"""
Webhook resource for webhook management.
"""

from typing import Any, Dict, List, Optional

from ..models.webhook import WebhookConfig, WebhookEvent, WebhookResponse
from .base import BaseResource


class WebhookResource(BaseResource):
    """Resource for webhook management."""

    def set_webhook(self, instance: str, webhook_config: WebhookConfig) -> WebhookResponse:
        """
        Set webhook configuration.

        Args:
            instance: Instance name
            webhook_config: Webhook configuration

        Returns:
            WebhookResponse with configuration status
        """
        response_data = self._post(
            f"/webhook/set/{instance}", json={"webhook": webhook_config.dict_for_api()}
        )
        return self._parse_response(response_data, WebhookResponse)

    def find_webhook(self, instance: str) -> WebhookResponse:
        """
        Find webhook configuration.

        Args:
            instance: Instance name

        Returns:
            WebhookResponse with current configuration
        """
        response_data = self._get(f"/webhook/find/{instance}")
        return self._parse_response(response_data, WebhookResponse)

    def set_websocket(
        self, instance: str, enabled: bool = True, events: Optional[List[WebhookEvent]] = None
    ) -> Dict[str, Any]:
        """
        Set WebSocket configuration.

        Args:
            instance: Instance name
            enabled: Whether WebSocket is enabled
            events: List of events to listen for

        Returns:
            Response data
        """
        return self._post(
            f"/websocket/set/{instance}",
            json={"websocket": {"enabled": enabled, "events": events or []}},
        )

    def find_websocket(self, instance: str) -> Dict[str, Any]:
        """
        Find WebSocket configuration.

        Args:
            instance: Instance name

        Returns:
            WebSocket configuration
        """
        return self._get(f"/websocket/find/{instance}")

    def set_rabbitmq(
        self, instance: str, enabled: bool = True, events: Optional[List[WebhookEvent]] = None
    ) -> Dict[str, Any]:
        """
        Set RabbitMQ configuration.

        Args:
            instance: Instance name
            enabled: Whether RabbitMQ is enabled
            events: List of events to listen for

        Returns:
            Response data
        """
        return self._post(
            f"/rabbitmq/set/{instance}",
            json={"rabbitmq": {"enabled": enabled, "events": events or []}},
        )

    def find_rabbitmq(self, instance: str) -> Dict[str, Any]:
        """
        Find RabbitMQ configuration.

        Args:
            instance: Instance name

        Returns:
            RabbitMQ configuration
        """
        return self._get(f"/rabbitmq/find/{instance}")

    def set_sqs(
        self, instance: str, enabled: bool = True, events: Optional[List[WebhookEvent]] = None
    ) -> Dict[str, Any]:
        """
        Set AWS SQS configuration.

        Args:
            instance: Instance name
            enabled: Whether SQS is enabled
            events: List of events to listen for

        Returns:
            Response data
        """
        return self._post(
            f"/sqs/set/{instance}", json={"sqs": {"enabled": enabled, "events": events or []}}
        )

    def find_sqs(self, instance: str) -> Dict[str, Any]:
        """
        Find AWS SQS configuration.

        Args:
            instance: Instance name

        Returns:
            SQS configuration
        """
        return self._get(f"/sqs/find/{instance}")
