from typing import Any


class OAuth2Exception(Exception):
    """Base OAUTH2 Exception."""

    def __init__(
            self,
            message: str,
            error_code: str | None = None,
            status_code: int | None = None,
            details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize AIS exception.

        Args:
            message: Error message
            error_code: Error code
            status_code: HTTP status code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}


class AISAuthorizationException(OAuth2Exception):
    """Exception raised for authorization-related errors."""

    def __init__(
            self,
            message: str,
            error_code: str | None = None,
            status_code: int | None = None,
            details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize authorization exception.

        Args:
            message: Error message
            error_code: Error code
            status_code: HTTP status code
            details: Additional error details
        """
        super().__init__(message, error_code, status_code, details)
