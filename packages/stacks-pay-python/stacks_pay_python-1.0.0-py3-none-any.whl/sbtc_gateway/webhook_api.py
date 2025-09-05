"""Webhook API for the sBTC Gateway SDK."""

from typing import Dict, Any, List, Optional

from .base import BaseAPI
from .types import Webhook, WebhookRequest


class WebhookAPI(BaseAPI):
    """API client for webhook management."""

    def create(self, webhook_data: WebhookRequest) -> Webhook:
        """Create a new webhook.
        
        Args:
            webhook_data: Webhook configuration
            
        Returns:
            Created webhook
        """
        response = self._make_request(
            'POST',
            '/api/webhooks',
            data=webhook_data.to_dict()
        )
        return Webhook(**response['webhook'])

    def retrieve(self, webhook_id: str) -> Webhook:
        """Retrieve a webhook by ID.
        
        Args:
            webhook_id: ID of the webhook
            
        Returns:
            Webhook details
        """
        response = self._make_request('GET', f'/api/webhooks/{webhook_id}')
        return Webhook(**response['webhook'])

    def list(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """List all webhooks with pagination.
        
        Args:
            page: Page number
            limit: Items per page
            status: Filter by status
            
        Returns:
            Dictionary containing webhooks and pagination info
        """
        params = {}
        if page is not None:
            params['page'] = page
        if limit is not None:
            params['limit'] = limit
        if status is not None:
            params['status'] = status

        response = self._make_request('GET', '/api/webhooks', params=params)
        
        return {
            'webhooks': [Webhook(**webhook) for webhook in response['webhooks']],
            'pagination': response['pagination']
        }

    def update(self, webhook_id: str, updates: Dict[str, Any]) -> Webhook:
        """Update a webhook.
        
        Args:
            webhook_id: ID of the webhook
            updates: Fields to update
            
        Returns:
            Updated webhook
        """
        response = self._make_request(
            'PUT',
            f'/api/webhooks/{webhook_id}',
            data=updates
        )
        return Webhook(**response['webhook'])

    def delete(self, webhook_id: str) -> None:
        """Delete a webhook.
        
        Args:
            webhook_id: ID of the webhook
        """
        self._make_request('DELETE', f'/api/webhooks/{webhook_id}')

    def test(self, webhook_id: str) -> Dict[str, Any]:
        """Test a webhook.
        
        Args:
            webhook_id: ID of the webhook
            
        Returns:
            Test results
        """
        return self._make_request('POST', f'/api/webhooks/{webhook_id}/test')

    def get_stats(self, webhook_id: Optional[str] = None) -> Dict[str, Any]:
        """Get webhook statistics.
        
        Args:
            webhook_id: Optional specific webhook ID
            
        Returns:
            Statistics data
        """
        url = f'/api/webhooks/{webhook_id}/stats' if webhook_id else '/api/webhooks/stats'
        response = self._make_request('GET', url)
        return response.get('stats', response)

    def retry(self, webhook_id: str) -> Dict[str, Any]:
        """Retry failed webhook events.
        
        Args:
            webhook_id: ID of the webhook
            
        Returns:
            Retry results
        """
        return self._make_request('POST', f'/api/webhooks/{webhook_id}/retry')
