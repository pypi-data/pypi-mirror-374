"""Type definitions for the sBTC Gateway SDK."""

from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Customer:
    """Customer information for payments."""
    email: Optional[str] = None
    name: Optional[str] = None
    id: Optional[str] = None


@dataclass 
class PaymentRequest:
    """Request data for creating a payment."""
    amount: int  # Amount in satoshis
    currency: Literal["sbtc", "btc", "stx"]
    description: str
    customer: Optional[Customer] = None
    metadata: Optional[Dict[str, Any]] = None
    webhook_url: Optional[str] = None
    redirect_url: Optional[str] = None
    expires_in: Optional[int] = None  # Seconds until payment expires
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API requests."""
        return asdict(self)


@dataclass
class WalletAddresses:
    """Wallet addresses for payment."""
    bitcoin: Optional[str] = None
    stacks: Optional[str] = None


@dataclass
class PaymentCustomer:
    """Customer information in payment response."""
    email: Optional[str] = None
    name: Optional[str] = None
    wallet_address: Optional[str] = None


@dataclass
class PaymentEvent:
    """Payment timeline event."""
    status: str
    timestamp: str
    transaction_hash: Optional[str] = None
    confirmations: Optional[int] = None


@dataclass
class Payment:
    """Payment object."""
    id: str
    amount: int
    currency: str
    status: Literal["pending", "paid", "completed", "failed", "expired"]
    description: str
    payment_url: str
    qr_code: str
    wallet_addresses: WalletAddresses
    expires_at: str
    created_at: str
    updated_at: str
    customer: Optional[PaymentCustomer] = None
    confirmations: Optional[int] = None
    transaction_hash: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timeline: Optional[List[PaymentEvent]] = None


@dataclass
class PaginationInfo:
    """Pagination information."""
    page: int
    limit: int
    total: int
    has_more: bool


@dataclass
class PaymentList:
    """List of payments with pagination."""
    payments: List[Payment]
    pagination: PaginationInfo


@dataclass
class Merchant:
    """Merchant information."""
    id: str
    name: str
    email: str
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    stacks_address: Optional[str] = None
    bitcoin_address: Optional[str] = None
    email_verified: bool = False
    verification_level: str = "none"
    created_at: Optional[str] = None


@dataclass
class WebhookEventData:
    """Webhook event data."""
    payment: Payment


@dataclass
class WebhookEvent:
    """Webhook event."""
    id: str
    type: Literal[
        "payment.created",
        "payment.paid", 
        "payment.completed",
        "payment.failed",
        "payment.expired"
    ]
    created: int
    data: WebhookEventData
    livemode: bool


@dataclass
class Webhook:
    """Webhook configuration."""
    id: str
    url: str
    events: List[str]
    status: Literal["active", "inactive"]
    secret: str
    created_at: str
    updated_at: str
    description: Optional[str] = None


@dataclass
class WebhookRequest:
    """Request data for creating/updating a webhook."""
    url: str
    events: List[str]
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API requests."""
        return asdict(self)


@dataclass
class APIKeyUsage:
    """API key usage statistics."""
    requests_today: int
    requests_this_month: int


@dataclass
class APIKey:
    """API key object."""
    id: str
    name: str
    key_prefix: str
    permissions: List[str]
    status: Literal["active", "inactive"]
    usage: APIKeyUsage
    created_at: str
    updated_at: str
    last_used: Optional[str] = None
    expires_at: Optional[str] = None


@dataclass
class APIKeyRequest:
    """Request data for creating an API key."""
    name: str
    permissions: List[str]
    expires_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API requests."""
        return asdict(self)


# API Response types
class APIResponse:
    """Base API response."""
    success: bool


class PaymentResponse(APIResponse):
    """Payment API response."""
    payment: Payment


class PaymentListResponse(APIResponse):
    """Payment list API response."""
    payments: List[Payment]
    pagination: PaginationInfo


class MerchantResponse(APIResponse):
    """Merchant API response."""
    merchant: Merchant
