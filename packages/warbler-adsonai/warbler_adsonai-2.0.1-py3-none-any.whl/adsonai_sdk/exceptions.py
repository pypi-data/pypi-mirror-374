"""
Exception classes for AdsonAI SDK - Version 2.0
Enhanced exception handling with detailed error information
"""

from typing import Optional, Dict, Any


class AdsonAIError(Exception):
    """
    Base exception for AdsonAI SDK
    
    All AdsonAI SDK exceptions inherit from this class
    """
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self):
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


class AuthenticationError(AdsonAIError):
    """
    Raised when API authentication fails
    
    This includes:
    - Invalid API key format
    - Expired API keys
    - Deactivated API keys
    - Missing authentication headers
    """
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class APIError(AdsonAIError):
    """
    Raised when API returns an error response
    
    Includes the HTTP status code and response details
    """
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        details = {}
        if status_code:
            details["status_code"] = status_code
        if response_data:
            details["response_data"] = response_data
            
        super().__init__(message, details)
        self.status_code = status_code
        self.response_data = response_data or {}
    
    @property
    def is_client_error(self) -> bool:
        """Check if error is a client error (4xx)"""
        return self.status_code is not None and 400 <= self.status_code < 500
    
    @property
    def is_server_error(self) -> bool:
        """Check if error is a server error (5xx)"""
        return self.status_code is not None and 500 <= self.status_code < 600
    
    @property
    def is_rate_limit_error(self) -> bool:
        """Check if error is a rate limit error (429)"""
        return self.status_code == 429


class ValidationError(AdsonAIError):
    """
    Raised when request validation fails
    
    This includes:
    - Invalid query parameters
    - Missing required fields
    - Out-of-range values
    - Invalid data formats
    """
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["invalid_value"] = str(value)
            
        super().__init__(message, details)
        self.field = field
        self.value = value


class NetworkError(AdsonAIError):
    """
    Raised when network connection fails
    
    This includes:
    - Connection timeouts
    - DNS resolution failures
    - Network unreachable errors
    - SSL certificate errors
    """
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        details = {}
        if original_error:
            details["original_error"] = str(original_error)
            details["original_error_type"] = type(original_error).__name__
            
        super().__init__(message, details)
        self.original_error = original_error


class RateLimitError(APIError):
    """
    Specific error for rate limit exceeded scenarios
    
    Includes retry information and rate limit details
    """
    def __init__(
        self, 
        message: str = "Rate limit exceeded", 
        retry_after: Optional[int] = None,
        limit: Optional[int] = None,
        remaining: Optional[int] = None,
        reset_time: Optional[int] = None
    ):
        details = {}
        if retry_after:
            details["retry_after_seconds"] = retry_after
        if limit:
            details["rate_limit"] = limit
        if remaining is not None:
            details["remaining_requests"] = remaining
        if reset_time:
            details["reset_time"] = reset_time
            
        super().__init__(message, status_code=429, response_data=details)
        self.retry_after = retry_after
        self.limit = limit
        self.remaining = remaining
        self.reset_time = reset_time


class ConfigurationError(AdsonAIError):
    """
    Raised when SDK configuration is invalid
    
    This includes:
    - Invalid base URLs
    - Missing environment variables
    - Invalid timeout values
    - Incompatible SDK versions
    """
    def __init__(self, message: str, config_key: Optional[str] = None, config_value: Optional[Any] = None):
        details = {}
        if config_key:
            details["config_key"] = config_key
        if config_value is not None:
            details["config_value"] = str(config_value)
            
        super().__init__(message, details)
        self.config_key = config_key
        self.config_value = config_value


class CacheError(AdsonAIError):
    """
    Raised when caching operations fail
    
    This includes:
    - Cache corruption
    - Cache storage full
    - Cache serialization errors
    """
    def __init__(self, message: str, operation: Optional[str] = None):
        details = {}
        if operation:
            details["cache_operation"] = operation
            
        super().__init__(message, details)
        self.operation = operation


class ContentTypeError(ValidationError):
    """
    Raised when content type validation fails
    
    Specific validation error for content type mismatches
    """
    def __init__(self, message: str, provided_type: Optional[str] = None, expected_types: Optional[list] = None):
        details = {}
        if provided_type:
            details["provided_type"] = provided_type
        if expected_types:
            details["expected_types"] = expected_types
            
        super().__init__(message, field="content_type")
        self.provided_type = provided_type
        self.expected_types = expected_types or []


class MatchingError(AdsonAIError):
    """
    Raised when ad matching process fails
    
    This includes:
    - AI matching service failures
    - Semantic analysis errors
    - Intent classification failures
    """
    def __init__(self, message: str, matching_stage: Optional[str] = None, query: Optional[str] = None):
        details = {}
        if matching_stage:
            details["matching_stage"] = matching_stage
        if query:
            details["query"] = query[:100]  # Limit query length in error details
            
        super().__init__(message, details)
        self.matching_stage = matching_stage
        self.query = query


# Helper functions for exception handling
def handle_api_response_error(response):
    """
    Convert HTTP response to appropriate AdsonAI exception
    
    Args:
        response: HTTP response object
        
    Raises:
        Appropriate AdsonAI exception based on status code
    """
    status_code = response.status_code
    
    try:
        response_data = response.json()
        error_message = response_data.get('error', f'HTTP {status_code} error')
    except:
        error_message = f'HTTP {status_code} error'
        response_data = {}
    
    if status_code == 401:
        raise AuthenticationError(error_message, details=response_data)
    elif status_code == 429:
        retry_after = response.headers.get('Retry-After')
        raise RateLimitError(
            error_message,
            retry_after=int(retry_after) if retry_after else None,
            limit=response_data.get('rate_limit'),
            remaining=response_data.get('remaining'),
            reset_time=response_data.get('reset_time')
        )
    elif 400 <= status_code < 500:
        raise ValidationError(error_message, details=response_data)
    elif 500 <= status_code < 600:
        raise APIError(error_message, status_code=status_code, response_data=response_data)
    else:
        raise APIError(error_message, status_code=status_code, response_data=response_data)


def is_retriable_error(error: Exception) -> bool:
    """
    Check if an error is retriable
    
    Args:
        error: Exception to check
        
    Returns:
        True if the error should be retried, False otherwise
    """
    if isinstance(error, NetworkError):
        return True
    
    if isinstance(error, APIError):
        # Retry on server errors and rate limits, but not client errors
        return error.is_server_error or error.is_rate_limit_error
    
    if isinstance(error, RateLimitError):
        return True
    
    # Don't retry authentication, validation, or configuration errors
    if isinstance(error, (AuthenticationError, ValidationError, ConfigurationError)):
        return False
    
    return False


def get_retry_delay(error: Exception, attempt: int, base_delay: float = 1.0) -> float:
    """
    Calculate retry delay for an error
    
    Args:
        error: Exception that occurred
        attempt: Current attempt number (1-based)
        base_delay: Base delay in seconds
        
    Returns:
        Delay in seconds before next retry
    """
    if isinstance(error, RateLimitError) and error.retry_after:
        return float(error.retry_after)
    
    # Exponential backoff with jitter
    import random
    delay = base_delay * (2 ** (attempt - 1))
    jitter = random.uniform(0.1, 0.3) * delay
    return delay + jitter


# Exception hierarchy summary for documentation
EXCEPTION_HIERARCHY = {
    'AdsonAIError': {
        'description': 'Base exception for all AdsonAI SDK errors',
        'subclasses': {
            'AuthenticationError': 'API authentication failures',
            'APIError': {
                'description': 'API response errors',
                'subclasses': {
                    'RateLimitError': 'Rate limit exceeded'
                }
            },
            'ValidationError': {
                'description': 'Request validation failures',
                'subclasses': {
                    'ContentTypeError': 'Content type validation errors'
                }
            },
            'NetworkError': 'Network connection failures',
            'ConfigurationError': 'SDK configuration errors',
            'CacheError': 'Caching operation failures',
            'MatchingError': 'Ad matching process failures'
        }
    }
}


# Export all exceptions
__all__ = [
    'AdsonAIError',
    'AuthenticationError', 
    'APIError',
    'ValidationError',
    'NetworkError',
    'RateLimitError',
    'ConfigurationError',
    'CacheError',
    'ContentTypeError',
    'MatchingError',
    'handle_api_response_error',
    'is_retriable_error',
    'get_retry_delay',
    'EXCEPTION_HIERARCHY'
]