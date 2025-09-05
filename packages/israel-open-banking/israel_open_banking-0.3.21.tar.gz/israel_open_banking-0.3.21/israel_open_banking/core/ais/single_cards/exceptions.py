"""
PSD2 AIS Exceptions.

This module contains exception classes specific to AIS operations
based on the Berlin Group NextGenPSD2 Framework v1.3.14 specification.
"""
from __future__ import annotations

from typing import Any, Optional


class AISSingleCardsException(Exception):
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


class AISConsentSingleCardsException(AISSingleCardsException):
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


class AISAccountSingleCardsException(AISSingleCardsException):
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


class AISTransactionSingleCardsException(AISSingleCardsException):
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


class AISBalanceSingleCardsException(AISSingleCardsException):
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
