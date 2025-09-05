"""Webhook utilities for the sBTC Gateway SDK."""

import json
import hmac
import hashlib
from typing import Union

from .types import WebhookEvent
from .exceptions import ValidationError


class WebhookUtils:
    """Utilities for handling webhooks."""

    @staticmethod
    def verify_signature(
        payload: Union[str, bytes],
        signature: str,
        secret: str
    ) -> bool:
        """Verify webhook signature."""
        try:
            if isinstance(payload, str):
                payload_bytes = payload.encode('utf-8')
            else:
                payload_bytes = payload
            
            computed_signature = hmac.new(
                secret.encode('utf-8'),
                payload_bytes,
                hashlib.sha256
            ).hexdigest()
            
            expected_signature = f"sha256={computed_signature}"
            
            return hmac.compare_digest(expected_signature, signature)
        except Exception:
            return False

    @staticmethod
    def parse_event(payload: str) -> WebhookEvent:
        """Parse webhook payload safely."""
        try:
            data = json.loads(payload)
            return WebhookEvent(**data)
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            raise ValidationError(f"Invalid webhook payload: {str(e)}")

    @staticmethod
    def verify_and_parse_event(
        payload: str,
        signature: str,
        secret: str
    ) -> WebhookEvent:
        """Verify signature and parse webhook event."""
        if not WebhookUtils.verify_signature(payload, signature, secret):
            raise ValidationError("Invalid webhook signature")
        
        return WebhookUtils.parse_event(payload)
