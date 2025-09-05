"""API Key management for the sBTC Gateway SDK."""

from typing import Dict, Any, List, Optional

from .base import BaseAPI
from .types import APIKey, APIKeyRequest


class APIKeyAPI(BaseAPI):
    """API client for API key management."""

    def generate(self, key_data: APIKeyRequest) -> Dict[str, Any]:
        """Generate a new API key.
        
        Args:
            key_data: API key configuration
            
        Returns:
            Dictionary containing API key info and the actual key
        """
        response = self._make_request(
            'POST',
            '/api/api-keys/generate',
            data=key_data.to_dict()
        )
        return {
            'api_key': APIKey(**response['apiKey']),
            'key': response['key']
        }

    def list(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """List all API keys with pagination.
        
        Args:
            page: Page number
            limit: Items per page
            status: Filter by status
            
        Returns:
            Dictionary containing API keys and pagination info
        """
        params = {}
        if page is not None:
            params['page'] = page
        if limit is not None:
            params['limit'] = limit
        if status is not None:
            params['status'] = status

        response = self._make_request('GET', '/api/api-keys', params=params)
        
        return {
            'api_keys': [APIKey(**key) for key in response['apiKeys']],
            'pagination': response['pagination']
        }

    def update(self, key_id: str, updates: Dict[str, Any]) -> APIKey:
        """Update an API key.
        
        Args:
            key_id: ID of the API key
            updates: Fields to update
            
        Returns:
            Updated API key
        """
        response = self._make_request(
            'PUT',
            f'/api/api-keys/{key_id}',
            data=updates
        )
        return APIKey(**response['apiKey'])

    def delete(self, key_id: str) -> None:
        """Delete an API key.
        
        Args:
            key_id: ID of the API key
        """
        self._make_request('DELETE', f'/api/api-keys/{key_id}')

    def regenerate(self, key_id: str) -> Dict[str, Any]:
        """Regenerate an API key.
        
        Args:
            key_id: ID of the API key
            
        Returns:
            Dictionary containing updated API key info and new key
        """
        response = self._make_request('POST', f'/api/api-keys/{key_id}/regenerate')
        return {
            'api_key': APIKey(**response['apiKey']),
            'key': response['key']
        }

    def activate(self, key_id: str) -> APIKey:
        """Activate an API key.
        
        Args:
            key_id: ID of the API key
            
        Returns:
            Updated API key
        """
        response = self._make_request('POST', f'/api/api-keys/{key_id}/activate')
        return APIKey(**response['apiKey'])

    def deactivate(self, key_id: str) -> APIKey:
        """Deactivate an API key.
        
        Args:
            key_id: ID of the API key
            
        Returns:
            Updated API key
        """
        response = self._make_request('POST', f'/api/api-keys/{key_id}/deactivate')
        return APIKey(**response['apiKey'])

    def get_usage(self, key_id: str) -> Dict[str, Any]:
        """Get API key usage statistics.
        
        Args:
            key_id: ID of the API key
            
        Returns:
            Usage statistics
        """
        response = self._make_request('GET', f'/api/api-keys/{key_id}/usage')
        return response['usage']

    def get_stats(self) -> Dict[str, Any]:
        """Get overall API key statistics.
        
        Returns:
            Statistics data
        """
        return self._make_request('GET', '/api/api-keys/stats')

    def test(self, key_id: str) -> Dict[str, Any]:
        """Test an API key.
        
        Args:
            key_id: ID of the API key
            
        Returns:
            Test results
        """
        return self._make_request('POST', f'/api/api-keys/{key_id}/test')

    def validate(self, key: str) -> Dict[str, Any]:
        """Validate an API key.
        
        Args:
            key: The API key to validate
            
        Returns:
            Validation results
        """
        return self._make_request('POST', '/api/api-keys/validate', data={'key': key})
