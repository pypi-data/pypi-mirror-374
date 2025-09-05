"""Payments API for the sBTC Gateway SDK."""

from typing import Dict, List, Optional, Any

from .base import BaseAPI
from .types import Payment, PaymentRequest, PaymentList


class PaymentsAPI(BaseAPI):
    """Payments API client."""

    def create(self, payment_data: PaymentRequest) -> Payment:
        """Create a new payment."""
        response = self._make_request('POST', '/api/v1/payments', data=payment_data.to_dict())
        return self._convert_to_payment(response['payment'])

    def retrieve(self, payment_id: str) -> Payment:
        """Retrieve a payment by ID."""
        response = self._make_request('GET', f'/api/v1/payments/{payment_id}')
        return self._convert_to_payment(response['payment'])

    def list(
        self,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        customer_email: Optional[str] = None
    ) -> PaymentList:
        """List all payments with pagination."""
        params: Dict[str, Any] = {
            'page': page,
            'limit': limit,
        }
        
        if status:
            params['status'] = status
        if customer_email:
            params['customer_email'] = customer_email
        
        response = self._make_request('GET', '/api/v1/payments', params=params)
        
        payments = [self._convert_to_payment(p) for p in response['payments']]
        
        return PaymentList(
            payments=payments,
            pagination=response['pagination']
        )

    def cancel(self, payment_id: str) -> Payment:
        """Cancel a pending payment."""
        response = self._make_request('POST', f'/api/v1/payments/{payment_id}/cancel')
        return self._convert_to_payment(response['payment'])

    def refund(self, payment_id: str, amount: Optional[int] = None) -> Payment:
        """Refund a completed payment."""
        data = {}
        if amount:
            data['amount'] = amount
        
        response = self._make_request(
            'POST', 
            f'/api/v1/payments/{payment_id}/refund',
            data=data if data else None
        )
        return self._convert_to_payment(response['payment'])

    def _convert_to_payment(self, data: Dict[str, Any]) -> Payment:
        """Convert API response data to Payment object."""
        from .types import WalletAddresses, PaymentCustomer, PaymentEvent
        
        # Convert wallet addresses
        wallet_data = data.get('wallet_addresses', {})
        wallet_addresses = WalletAddresses(
            bitcoin=wallet_data.get('bitcoin'),
            stacks=wallet_data.get('stacks')
        )
        
        # Convert customer data
        customer = None
        if data.get('customer'):
            customer_data = data['customer']
            customer = PaymentCustomer(
                email=customer_data.get('email'),
                name=customer_data.get('name'),
                wallet_address=customer_data.get('wallet_address')
            )
        
        # Convert timeline events
        timeline = None
        if data.get('timeline'):
            timeline = [
                PaymentEvent(
                    status=event['status'],
                    timestamp=event['timestamp'],
                    transaction_hash=event.get('transaction_hash'),
                    confirmations=event.get('confirmations')
                )
                for event in data['timeline']
            ]
        
        return Payment(
            id=data['id'],
            amount=data['amount'],
            currency=data['currency'],
            status=data['status'],
            description=data['description'],
            payment_url=data['payment_url'],
            qr_code=data['qr_code'],
            wallet_addresses=wallet_addresses,
            expires_at=data['expires_at'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            customer=customer,
            confirmations=data.get('confirmations'),
            transaction_hash=data.get('transaction_hash'),
            metadata=data.get('metadata'),
            timeline=timeline
        )
