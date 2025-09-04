"""
Main client for the Israel Open Banking SDK.

This module provides the primary interface for interacting with
Open Banking APIs, handling authentication, requests, and responses.
"""

import logging
import time
from typing import Any

import httpx
import requests

from .config import OpenBankingConfig
from .exceptions import (
    APIError,
    AuthenticationError,
    NetworkError,
    RateLimitError,
    TimeoutError,
)


class OpenBankingClient:
    """Main client for interacting with Open Banking APIs."""

    def __init__(self, config: OpenBankingConfig | None = None) -> None:
        """
        Initialize the Open Banking client.

        Args:
            config: Configuration object (will create default if not provided)
        """
        self.config = config or OpenBankingConfig()
        self.logger = self._setup_logging()

        # Initialize HTTP clients
        self._session = requests.Session()
        self._async_client: httpx.AsyncClient | None = None

        # Set up session defaults
        self._session.headers.update(
            {
                "User-Agent": "Open-Banking/0.1.0",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

        # Authentication state
        self._access_token: str | None = None
        self._token_expires_at: float | None = None

    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger("open_banking_sdk")

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(self.config.log_format)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        logger.setLevel(getattr(logging, self.config.log_level.upper()))
        return logger

    def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                timeout=self.config.api_timeout,
                headers={
                    "User-Agent": "Open-Banking/0.1.0",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
        return self._async_client

    def _is_token_valid(self) -> bool:
        """Check if the current access token is still valid."""
        if not self._access_token or not self._token_expires_at:
            return False
        return time.time() < self._token_expires_at

    def _authenticate(self) -> None:
        """
        Authenticate with the Open Banking API.

        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            auth_data = {
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "grant_type": "client_credentials",
            }

            response = self._session.post(
                f"{self.config.api_base_url}/oauth/token",
                data=auth_data,
                timeout=self.config.api_timeout,
            )

            if response.status_code != 200:
                raise AuthenticationError(
                    f"Authentication failed with status {response.status_code}",
                    error_code=f"HTTP_{response.status_code}",
                    details={
                        "status_code": response.status_code,
                        "response_data": response.json() if response.content else None,
                    },
                )

            token_data = response.json()
            self._access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)
            self._token_expires_at = time.time() + expires_in

            self.logger.info("Successfully authenticated with Open Banking API")

        except requests.RequestException as e:
            raise NetworkError(f"Network error during authentication: {e}")
        except Exception as e:
            raise AuthenticationError(f"Authentication failed: {e}")

    def _ensure_authenticated(self) -> None:
        """Ensure we have a valid access token."""
        if not self._is_token_valid():
            self._authenticate()

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        """
        Make an HTTP request with authentication and error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            headers: Additional headers

        Returns:
            HTTP response object

        Raises:
            APIError: If the API returns an error
            NetworkError: If there's a network error
            TimeoutError: If the request times out
        """
        self._ensure_authenticated()

        url = f"{self.config.api_base_url}{endpoint}"
        request_headers = headers or {}

        if self._access_token:
            request_headers["Authorization"] = f"Bearer {self._access_token}"

        try:
            response = self._session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=request_headers,
                timeout=self.config.api_timeout,
            )

            # Handle rate limiting
            if response.status_code == 429:
                int(response.headers.get("Retry-After", 60))
                raise RateLimitError(
                    "Rate limit exceeded",
                    status_code=response.status_code,
                    response_data=response.json() if response.content else None,
                )

            # Handle other error status codes
            if response.status_code >= 400:
                raise APIError(
                    f"API request failed with status {response.status_code}",
                    status_code=response.status_code,
                    response_data=response.json() if response.content else None,
                )

            return response

        except requests.Timeout:
            raise TimeoutError("Request timed out")
        except requests.RequestException as e:
            raise NetworkError(f"Network error: {e}")

    async def _make_async_request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """
        Make an async HTTP request with authentication and error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            headers: Additional headers

        Returns:
            HTTP response object

        Raises:
            APIError: If the API returns an error
            NetworkError: If there's a network error
            TimeoutError: If the request times out
        """
        self._ensure_authenticated()

        client = self._get_async_client()
        url = f"{self.config.api_base_url}{endpoint}"
        request_headers = headers or {}

        if self._access_token:
            request_headers["Authorization"] = f"Bearer {self._access_token}"

        try:
            response = await client.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=request_headers,
            )

            # Handle rate limiting
            if response.status_code == 429:
                int(response.headers.get("Retry-After", 60))
                raise RateLimitError(
                    "Rate limit exceeded",
                    status_code=response.status_code,
                    response_data=response.json() if response.content else None,
                )

            # Handle other error status codes
            if response.status_code >= 400:
                raise APIError(
                    f"API request failed with status {response.status_code}",
                    status_code=response.status_code,
                    response_data=response.json() if response.content else None,
                )

            return response

        except httpx.TimeoutException:
            raise TimeoutError("Request timed out")
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}")

    def get(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Make a GET request.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            Response data as dictionary
        """
        response = self._make_request("GET", endpoint, params=params)
        return response.json()

    def post(self, endpoint: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Make a POST request.

        Args:
            endpoint: API endpoint path
            data: Request body data

        Returns:
            Response data as dictionary
        """
        response = self._make_request("POST", endpoint, data=data)
        return response.json()

    async def aget(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Make an async GET request.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            Response data as dictionary
        """
        response = await self._make_async_request("GET", endpoint, params=params)
        return response.json()

    async def apost(
        self, endpoint: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Make an async POST request.

        Args:
            endpoint: API endpoint path
            data: Request body data

        Returns:
            Response data as dictionary
        """
        response = await self._make_async_request("POST", endpoint, data=data)
        return response.json()

    def close(self) -> None:
        """Close the client and clean up resources."""
        if self._session:
            self._session.close()
        if self._async_client:
            self._async_client.close()

    async def aclose(self) -> None:
        """Close the async client and clean up resources."""
        if self._async_client:
            await self._async_client.aclose()

    def __enter__(self) -> "OpenBankingClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    async def __aenter__(self) -> "OpenBankingClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.aclose()
