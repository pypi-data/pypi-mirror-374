class APIError(Exception):
    """Base class for all API errors"""
    pass

class AuthenticationError(APIError):
    """Invalid authentication credentials"""
    pass

class InvalidRequestError(APIError):
    """Invalid request parameters"""
    pass

class RateLimitError(APIError):
    """Rate limit exceeded"""
    pass

class ServiceUnavailableError(APIError):
    """Service unavailable"""
    pass