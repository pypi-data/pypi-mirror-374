"""
Custom exceptions for the Israel Open Banking SDK.

This module defines all custom exceptions used throughout the SDK
to provide clear error handling and debugging information.
"""

from typing import Any

import requests

from israel_open_banking.core.ais.general.exceptions import AISException, AISRateLimitException, \
    AISConsentExpiredException
from israel_open_banking.core.ais.savings_and_loans.exceptions import AISSavingsAndLoansException
from israel_open_banking.core.ais.securities.exceptions import AISSecuritiesException
from israel_open_banking.core.ais.single_cards import AISSingleCardsException
from israel_open_banking.core.oauth.exceptions import OAuth2Exception


class OpenBankingException(Exception):
    """Base exception for all Open Banking SDK errors."""

    def __init__(
            self,
            message: str,
            error_code: str | None = None,
            details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the exception with error details.

        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
            details: Optional dictionary with additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ConfigurationError(OpenBankingException):
    """Raised when there are configuration issues."""

    pass


class AuthenticationError(OpenBankingException):
    """Raised when authentication fails."""

    pass


class AuthorizationError(OpenBankingException):
    """Raised when authorization is insufficient for the requested operation."""

    pass


class APIError(OpenBankingException):
    """Raised when the API returns an error response."""

    def __init__(
            self,
            message: str,
            status_code: int | None = None,
            response_data: dict[str, Any] | None = None,
            **kwargs: Any,
    ) -> None:
        """
        Initialize API error with HTTP status and response data.

        Args:
            message: Error message
            status_code: HTTP status code
            response_data: Response data from the API
            **kwargs: Additional arguments passed to parent
        """
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.response_data = response_data or {}


class RateLimitError(APIError):
    """Raised when API rate limits are exceeded."""

    pass


class ValidationError(OpenBankingException):
    """Raised when data validation fails."""

    pass


class NetworkError(OpenBankingException):
    """Raised when network communication fails."""

    pass


class TimeoutError(OpenBankingException):
    """Raised when API requests timeout."""

    pass


def raise_from_response(
        resp: requests.Response, default_exc: type[
            AISException | OAuth2Exception | AISSavingsAndLoansException | AISSingleCardsException | AISSecuritiesException]
) -> None:
    """
    Raise an appropriate AIS exception based on HTTP status & payload.
    Extracted from pepper_ais_client.py to avoid circular imports.
    """
    status = resp.status_code
    msg = resp.text or resp.reason

    if status == 404:
        raise default_exc(msg, status_code=status)
    if status == 429:
        retry = int(resp.headers.get("Retry-After", "0")) or None
        raise AISRateLimitException(msg, status_code=status, retry_after=retry)
    if status == 401:
        raise AISConsentExpiredException(msg, status_code=status)
    raise default_exc(msg, status_code=status)
