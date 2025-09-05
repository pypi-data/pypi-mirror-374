"""CTS API exceptions."""


class CtsError(Exception):
    """Base class for CTS errors."""


class ApiConnectionError(CtsError):
    """Exception raised when an error happend when connecting to the API."""


class InvalidTokenError(CtsError):
    """Exception raised when the auth token is invalid."""


class BadRequestError(CtsError):
    """Exception raised when the request is invalid (missing or invalid parameters)."""


class TooManyRequestsError(CtsError):
    """Exception raised when too many requests have been made."""


class TechnicalError(CtsError):
    """Exception raised when a technical exception occured."""
