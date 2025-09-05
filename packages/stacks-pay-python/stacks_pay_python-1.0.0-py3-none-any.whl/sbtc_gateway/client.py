"""Main client for the StacksPay SDK."""

from typing import Optional

from .payments import PaymentsAPI
from .merchant import MerchantAPI
from .webhook_api import WebhookAPI
from .api_key import APIKeyAPI
from .webhooks import WebhookUtils


class SBTCGateway:
    """Main StacksPay client."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.stackspay.com",
        timeout: int = 30,
        retries: int = 3
    ):
        """Initialize the StacksPay client.
        
        Args:
            api_key: Your API key (starts with sk_test_ or sk_live_)
            base_url: API base URL (default: https://api.stackspay.com)
            timeout: Request timeout in seconds (default: 30)
            retries: Number of retry attempts (default: 3)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.retries = retries
        
        # Initialize API clients
        self.payments = PaymentsAPI(api_key, base_url, timeout, retries)
        self.merchant = MerchantAPI(api_key, base_url, timeout, retries)
        self.webhooks = WebhookAPI(api_key, base_url, timeout, retries)
        self.api_keys = APIKeyAPI(api_key, base_url, timeout, retries)
        
        # Webhook utilities (static methods)
        self.webhook_utils = WebhookUtils
