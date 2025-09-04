"""
Message resource for sending messages.
"""

from typing import Any, Dict, List, Optional

from ..models.message import (
    AudioMessage,
    ContactCard,
    ContactMessage,
    LocationMessage,
    MediaMessage,
    MessageResponse,
    ReactionMessage,
    StickerMessage,
    TextMessage,
)
from .base import BaseResource


class MessageResource(BaseResource):
    """Resource for sending messages."""

    def send_text(self, instance: str, number: str, text: str, **kwargs: Any) -> MessageResponse:
        """
        Send a text message.

        Args:
            instance: Instance name
            number: Recipient phone number
            text: Text message content
            **kwargs: Additional message options

        Returns:
            MessageResponse with sent message details
        """
        message = TextMessage(number=number, text=text, **kwargs)
        response_data = self._post(f"/message/sendText/{instance}", json=message.dict_for_api())
        return self._parse_response(response_data, MessageResponse)

    def send_media(
        self,
        instance: str,
        number: str,
        mediatype: str,
        media: str,
        caption: Optional[str] = None,
        **kwargs: Any,
    ) -> MessageResponse:
        """
        Send a media message (image, video, document).

        Args:
            instance: Instance name
            number: Recipient phone number
            mediatype: Type of media (image, video, document)
            media: URL or base64 of the media
            caption: Optional caption
            **kwargs: Additional options

        Returns:
            MessageResponse with sent message details
        """
        message = MediaMessage(
            number=number, mediatype=mediatype, media=media, caption=caption, **kwargs
        )
        response_data = self._post(f"/message/sendMedia/{instance}", json=message.dict_for_api())
        return self._parse_response(response_data, MessageResponse)

    def send_audio(self, instance: str, number: str, audio: str, **kwargs: Any) -> MessageResponse:
        """
        Send an audio message.

        Args:
            instance: Instance name
            number: Recipient phone number
            audio: URL or base64 of the audio
            **kwargs: Additional options

        Returns:
            MessageResponse
        """
        message = AudioMessage(number=number, audio=audio, **kwargs)
        response_data = self._post(
            f"/message/sendWhatsAppAudio/{instance}", json=message.dict_for_api()
        )
        return self._parse_response(response_data, MessageResponse)

    def send_location(
        self,
        instance: str,
        number: str,
        name: str,
        address: str,
        latitude: float,
        longitude: float,
        **kwargs: Any,
    ) -> MessageResponse:
        """
        Send a location message.

        Args:
            instance: Instance name
            number: Recipient phone number
            name: Location name
            address: Location address
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            **kwargs: Additional options

        Returns:
            MessageResponse
        """
        message = LocationMessage(
            number=number,
            name=name,
            address=address,
            latitude=latitude,
            longitude=longitude,
            **kwargs,
        )
        response_data = self._post(f"/message/sendLocation/{instance}", json=message.dict_for_api())
        return self._parse_response(response_data, MessageResponse)

    def send_contact(
        self, instance: str, number: str, contacts: List[Dict[str, Any]], **kwargs: Any
    ) -> MessageResponse:
        """
        Send contact(s).

        Args:
            instance: Instance name
            number: Recipient phone number
            contacts: List of contact dictionaries
            **kwargs: Additional options

        Returns:
            MessageResponse
        """
        contact_cards = [ContactCard(**contact) for contact in contacts]
        message = ContactMessage(number=number, contact=contact_cards, **kwargs)
        response_data = self._post(f"/message/sendContact/{instance}", json=message.dict_for_api())
        return self._parse_response(response_data, MessageResponse)

    def send_reaction(self, instance: str, key: Dict[str, Any], reaction: str) -> MessageResponse:
        """
        Send a reaction to a message.

        Args:
            instance: Instance name
            key: Message key to react to
            reaction: Emoji reaction

        Returns:
            MessageResponse
        """
        message = ReactionMessage(key=key, reaction=reaction)
        response_data = self._post(f"/message/sendReaction/{instance}", json=message.dict_for_api())
        return self._parse_response(response_data, MessageResponse)

    def send_sticker(
        self, instance: str, number: str, sticker: str, **kwargs: Any
    ) -> MessageResponse:
        """
        Send a sticker.

        Args:
            instance: Instance name
            number: Recipient phone number
            sticker: URL or base64 of the sticker
            **kwargs: Additional options

        Returns:
            MessageResponse
        """
        message = StickerMessage(number=number, sticker=sticker, **kwargs)
        response_data = self._post(f"/message/sendSticker/{instance}", json=message.dict_for_api())
        return self._parse_response(response_data, MessageResponse)

    def send_poll(
        self,
        instance: str,
        number: str,
        name: str,
        values: List[str],
        selectable_count: int = 1,
        **kwargs: Any,
    ) -> MessageResponse:
        """
        Send a poll message.

        Args:
            instance: Instance name
            number: Recipient phone number
            name: Poll question
            values: Poll options
            selectable_count: How many options can be selected
            **kwargs: Additional options

        Returns:
            MessageResponse
        """
        response_data = self._post(
            f"/message/sendPoll/{instance}",
            json={
                "number": number,
                "name": name,
                "values": values,
                "selectableCount": selectable_count,
                **kwargs,
            },
        )
        return self._parse_response(response_data, MessageResponse)

    def send_status(
        self,
        instance: str,
        type: str,
        content: str,
        all_contacts: bool = False,
        status_jid_list: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> MessageResponse:
        """
        Send a status/story.

        Args:
            instance: Instance name
            type: Status type (text, image, video, audio)
            content: Content (text or URL)
            all_contacts: Send to all contacts
            status_jid_list: Specific contacts to send to
            **kwargs: Additional options

        Returns:
            MessageResponse
        """
        response_data = self._post(
            f"/message/sendStatus/{instance}",
            json={
                "type": type,
                "content": content,
                "allContacts": all_contacts,
                "statusJidList": status_jid_list,
                **kwargs,
            },
        )
        return self._parse_response(response_data, MessageResponse)

    # Async methods
    async def asend_text(
        self, instance: str, number: str, text: str, **kwargs: Any
    ) -> MessageResponse:
        """Async version of send_text."""
        message = TextMessage(number=number, text=text, **kwargs)
        response_data = await self._apost(
            f"/message/sendText/{instance}", json=message.dict_for_api()
        )
        return self._parse_response(response_data, MessageResponse)
