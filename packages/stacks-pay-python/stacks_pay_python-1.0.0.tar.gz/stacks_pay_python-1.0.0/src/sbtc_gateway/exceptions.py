"""Exception classes for the sBTC Gateway SDK."""

from typing import Optional, Any


class SBTCGatewayError(Exception):
    """Base exception class for sBTC Gateway SDK."""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details

    def __str__(self) -> str:
        if self.code:
            return f"{self.code}: {self.message}"
        return self.message


class APIError(SBTCGatewayError):
    """Exception raised for API errors."""
    pass


class AuthenticationError(SBTCGatewayError):
    """Exception raised for authentication errors."""
    pass


class ValidationError(SBTCGatewayError):
    """Exception raised for validation errors."""
    pass


class NetworkError(SBTCGatewayError):
    """Exception raised for network errors."""
    pass


class RateLimitError(SBTCGatewayError):
    """Exception raised when rate limit is exceeded."""
    pass
