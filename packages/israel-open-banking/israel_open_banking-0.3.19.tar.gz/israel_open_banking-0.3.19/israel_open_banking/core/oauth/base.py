"""
PSD2 AIS Base Classes.

This module contains abstract base classes that define the interface
for PSD2-compliant Account Information Services.

All banks and credit card providers should implement these base classes
to ensure PSD2 compliance and interoperability.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from israel_open_banking.core.oauth.models import TokenResponse

if TYPE_CHECKING:
    from core.client import OpenBankingClient


class OAuth2BaseClient(ABC):
    """
    Abstract base class for OAuth2 clients.

    This class defines the interface that all OAuth2 clients must implement
    to manage OAuth2 tokens for Account Information Services (AIS).
    """

    def __init__(self, client: "OpenBankingClient") -> None:
        """
        Initialize the AIS base client.

        Args:
            client: The underlying OpenBankingClient instance
        """
        self.client = client
        # These will be set by concrete implementations
        self.oauth2: OAuth2Manager | None = None

    @abstractmethod
    def refresh_access_token(self) -> TokenResponse:
        """
        Get refresh token.

        Returns:
            Refresh token string
        """
        pass


class OAuth2Manager(ABC):
    """
    Abstract base class for OAuth2 management in AIS.

    This class defines the interface for managing OAuth2 tokens,
    including token retrieval and refresh.
    """

    def __init__(self, client: OAuth2BaseClient) -> None:
        """
        Initialize the OAuth2 manager.

        Args:
            client: The base client instance that this manager will operate on.
        """
        self.client = client

    @abstractmethod
    def get_access_token(self) -> str:
        """
        Get access token.

        Returns:
            Access token string
        """
        pass

    @abstractmethod
    def refresh_access_token(self) -> TokenResponse:
        """
        Refresh access token.

        Returns:
            New access token string
        """
        pass
