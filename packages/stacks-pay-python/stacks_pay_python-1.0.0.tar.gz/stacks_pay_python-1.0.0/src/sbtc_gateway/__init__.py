"""
StacksPay Python SDK

Official Python SDK for StacksPay.
Accept Bitcoin and STX payments with ease.
"""

from .client import SBTCGateway
from .exceptions import SBTCGatewayError, APIError, AuthenticationError, ValidationError
from .types import (
    Payment, PaymentRequest, Customer, Merchant, WebhookEvent, 
    Webhook, WebhookRequest, APIKey, APIKeyRequest
)
from .webhooks import WebhookUtils

__version__ = "1.0.0"
__author__ = "StacksPay Team"
__email__ = "developers@stackspay.com"

__all__ = [
    "SBTCGateway",
    "SBTCGatewayError",
    "APIError", 
    "AuthenticationError",
    "ValidationError",
    "Payment",
    "PaymentRequest",
    "Customer",
    "Merchant",
    "WebhookEvent",
    "Webhook",
    "WebhookRequest",
    "APIKey",
    "APIKeyRequest",
    "WebhookUtils",
]
