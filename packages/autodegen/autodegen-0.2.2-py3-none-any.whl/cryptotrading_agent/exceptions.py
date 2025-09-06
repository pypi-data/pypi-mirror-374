"""Exception classes for CryptoTrading Agent."""

from __future__ import annotations


class TradingAgentError(Exception):
    """Base exception for all trading agent errors."""
    
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class APIError(TradingAgentError):
    """Raised when external API calls fail."""
    
    def __init__(self, message: str, status_code: int | None = None, details: dict | None = None):
        super().__init__(message, details)
        self.status_code = status_code


class ValidationError(TradingAgentError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: str | None = None, details: dict | None = None):
        super().__init__(message, details)
        self.field = field


class ConfigurationError(TradingAgentError):
    """Raised when configuration is invalid."""
    pass


class RateLimitError(APIError):
    """Raised when API rate limits are exceeded."""
    
    def __init__(self, message: str, retry_after: int | None = None, details: dict | None = None):
        super().__init__(message, status_code=429, details=details)
        self.retry_after = retry_after


class CircuitBreakerOpenError(TradingAgentError):
    """Raised when circuit breaker is in OPEN state."""
    
    def __init__(self, message: str = "Circuit breaker is open - too many recent failures"):
        super().__init__(message)


class TimeoutError(TradingAgentError):
    """Raised when operations timeout."""
    
    def __init__(self, message: str, timeout_seconds: float | None = None):
        super().__init__(message)
        self.timeout_seconds = timeout_seconds