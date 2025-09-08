"""Custom exceptions for WavespeedMCP."""


class WavespeedAPIError(Exception):
    """Base exception for Wavespeed API errors."""
    pass


class WavespeedAuthError(WavespeedAPIError):
    """Authentication related errors."""
    pass


class WavespeedRequestError(WavespeedAPIError):
    """Request related errors."""
    pass


class WavespeedTimeoutError(WavespeedAPIError):
    """Timeout related errors."""
    pass


class WavespeedValidationError(WavespeedAPIError):
    """Validation related errors."""
    pass 


class WavespeedMcpError(WavespeedAPIError):
    """General MCP related errors."""
    pass
