"""Merchant API for the sBTC Gateway SDK."""

from typing import Dict, Optional, Any

from .base import BaseAPI
from .types import Merchant


class MerchantAPI(BaseAPI):
    """Merchant API client."""

    def get_current(self) -> Merchant:
        """Get current merchant information."""
        response = self._make_request('GET', '/api/auth/me')
        return self._convert_to_merchant(response['merchant'])

    def update(
        self,
        name: Optional[str] = None,
        business_type: Optional[str] = None,
        website: Optional[str] = None,
        stacks_address: Optional[str] = None,
        bitcoin_address: Optional[str] = None
    ) -> Merchant:
        """Update merchant information."""
        data = {}
        
        if name is not None:
            data['name'] = name
        if business_type is not None:
            data['business_type'] = business_type
        if website is not None:
            data['website'] = website
        if stacks_address is not None:
            data['stacks_address'] = stacks_address
        if bitcoin_address is not None:
            data['bitcoin_address'] = bitcoin_address
        
        response = self._make_request('PATCH', '/api/auth/me', data=data)
        return self._convert_to_merchant(response['merchant'])

    def _convert_to_merchant(self, data: Dict[str, Any]) -> Merchant:
        """Convert API response data to Merchant object."""
        return Merchant(
            id=data['id'],
            name=data['name'],
            email=data['email'],
            business_name=data.get('business_name'),
            business_type=data.get('business_type'),
            stacks_address=data.get('stacks_address'),
            bitcoin_address=data.get('bitcoin_address'),
            email_verified=data.get('email_verified', False),
            verification_level=data.get('verification_level', 'none'),
            created_at=data.get('created_at')
        )
