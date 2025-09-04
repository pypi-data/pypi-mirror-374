"""
PSD2 AIS Exceptions.

This module contains exception classes specific to AIS operations
based on the Berlin Group NextGenPSD2 Framework v1.3.14 specification.
"""

from typing import Any, Optional


class AISException(Exception):
    """Base exception for AIS operations."""

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


class AISConsentException(AISException):
    """Exception raised for consent-related errors."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize consent exception.

        Args:
            message: Error message
            error_code: Error code
            status_code: HTTP status code
            details: Additional error details
        """
        super().__init__(message, error_code, status_code, details)


class AISAccountException(AISException):
    """Exception raised for account-related errors."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize account exception.

        Args:
            message: Error message
            error_code: Error code
            status_code: HTTP status code
            details: Additional error details
        """
        super().__init__(message, error_code, status_code, details)


class AISTransactionException(AISException):
    """Exception raised for transaction-related errors."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize transaction exception.

        Args:
            message: Error message
            error_code: Error code
            status_code: HTTP status code
            details: Additional error details
        """
        super().__init__(message, error_code, status_code, details)


class AISBalanceException(AISException):
    """Exception raised for balance-related errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Initialize balance exception.

        Args:
            message: Error message
            error_code: Error code
            status_code: HTTP status code
            details: Additional error details
        """
        super().__init__(message, error_code, status_code, details)


class AISAuthenticationException(AISException):
    """Exception raised for authentication-related errors."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize authentication exception.

        Args:
            message: Error message
            error_code: Error code
            status_code: HTTP status code
            details: Additional error details
        """
        super().__init__(message, error_code, status_code, details)




class AISValidationException(AISException):
    """Exception raised for validation errors."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize validation exception.

        Args:
            message: Error message
            error_code: Error code
            status_code: HTTP status code
            details: Additional error details
        """
        super().__init__(message, error_code, status_code, details)


class AISRateLimitException(AISException):
    """Exception raised for rate limiting errors."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
        retry_after: int | None = None,
    ) -> None:
        """
        Initialize rate limit exception.

        Args:
            message: Error message
            error_code: Error code
            status_code: HTTP status code
            details: Additional error details
            retry_after: Retry after seconds
        """
        super().__init__(message, error_code, status_code, details)
        self.retry_after = retry_after


class AISConsentExpiredException(AISConsentException):
    """Exception raised when consent has expired."""

    def __init__(
        self,
        message: str = "Consent has expired",
        error_code: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize consent expired exception.

        Args:
            message: Error message
            error_code: Error code
            status_code: HTTP status code
            details: Additional error details
        """
        super().__init__(message, error_code, status_code, details)


class AISConsentRevokedException(AISConsentException):
    """Exception raised when consent has been revoked."""

    def __init__(
        self,
        message: str = "Consent has been revoked",
        error_code: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize consent revoked exception.

        Args:
            message: Error message
            error_code: Error code
            status_code: HTTP status code
            details: Additional error details
        """
        super().__init__(message, error_code, status_code, details)


class AISAccountNotFoundException(AISAccountException):
    """Exception raised when account is not found."""

    def __init__(
        self,
        account_id: str,
        message: str | None = None,
        error_code: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize account not found exception.

        Args:
            account_id: Account identifier
            message: Error message
            error_code: Error code
            status_code: HTTP status code
            details: Additional error details
        """
        if message is None:
            message = f"Account '{account_id}' not found"
        super().__init__(message, error_code, status_code, details)
        self.account_id = account_id


class AISTransactionNotFoundException(AISTransactionException):
    """Exception raised when transaction is not found."""

    def __init__(
        self,
        transaction_id: str,
        message: str | None = None,
        error_code: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize transaction not found exception.

        Args:
            transaction_id: Transaction identifier
            message: Error message
            error_code: Error code
            status_code: HTTP status code
            details: Additional error details
        """
        if message is None:
            message = f"Transaction '{transaction_id}' not found"
        super().__init__(message, error_code, status_code, details)
        self.transaction_id = transaction_id
