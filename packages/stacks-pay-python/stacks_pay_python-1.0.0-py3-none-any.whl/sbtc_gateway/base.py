"""Base API client for the StacksPay SDK."""

import json
import time
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin, urlencode

import requests

from .exceptions import (
    SBTCGatewayError,
    APIError,
    AuthenticationError,
    ValidationError,
    NetworkError,
    RateLimitError,
)


class BaseAPI:
    """Base API client with common functionality."""
    
    def __init__(
        self, 
        api_key: str,
        base_url: str = "https://api.stackspay.com",
        timeout: int = 30,
        retries: int = 3
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retries = retries
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'stacks-pay-python/1.0.0'
        })

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API."""
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        
        # Prepare request arguments
        kwargs = {
            'timeout': self.timeout,
            'params': params
        }
        
        if data is not None:
            kwargs['data'] = json.dumps(data)
        
        # Retry logic
        last_exception = None
        for attempt in range(self.retries + 1):
            try:
                response = self.session.request(method, url, **kwargs)
                return self._handle_response(response)
                
            except (requests.ConnectionError, requests.Timeout) as e:
                last_exception = e
                if attempt < self.retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise NetworkError(f"Network error after {self.retries + 1} attempts: {str(e)}")
            
            except requests.RequestException as e:
                raise NetworkError(f"Request error: {str(e)}")
        
        # Should not reach here, but just in case
        if last_exception:
            raise NetworkError(f"Network error: {str(last_exception)}")
        
        # This should never be reached, but needed for type checking
        raise NetworkError("Unexpected error in request handling")

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle the HTTP response."""
        try:
            data = response.json()
        except ValueError:
            raise APIError(f"Invalid JSON response: {response.text}")
        
        # Handle error responses
        if not response.ok:
            error_message = data.get('error', f'HTTP {response.status_code}')
            error_code = data.get('code')
            error_details = data.get('details')
            
            if response.status_code == 401:
                raise AuthenticationError(error_message, error_code, error_details)
            elif response.status_code == 400:
                raise ValidationError(error_message, error_code, error_details)
            elif response.status_code == 429:
                raise RateLimitError(error_message, error_code, error_details)
            else:
                raise APIError(error_message, error_code, error_details)
        
        return data
