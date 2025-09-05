class WNException(Exception):
    """Base exception for Wiener Netze Smart Meter integration."""


class WNAuthException(WNException):
    """Exception for authentication errors."""


class WNApiException(WNException):
    """Exception for API errors."""


class WNNetworkException(WNException):
    """Exception for Network errors."""
