from __future__ import annotations

from israel_open_banking.core.oauth.base import OAuth2BaseClient
from israel_open_banking.core.oauth.models import TokenResponse
from israel_open_banking.oauth2.mizrahi.clients.mizrahi_oauth2_manager import MizrahiOAuth2Manager
from israel_open_banking.oauth2.mizrahi.services.mizrahi_bank_auth_service import MizrahiBankAuthService

"""Mizrahi‑Bank concrete implementation of the PSD2 AIS abstraction layer.

This file wires the bank‑specific HTTP wrapper (``MizrahiBankService``)
into the generic AIS interfaces so the rest of the application can stay
vendor‑agnostic.

All network exceptions are captured and remapped to domain‑specific AIS
exceptions defined in ``israel_open_banking.core.ais.exceptions``.
"""


class MizrahiOAuth2Client(OAuth2BaseClient):
    """PSD2‑compliant AIS adapter for Mizrahi Bank."""

    def __init__(self, service: MizrahiBankAuthService) -> None:
        super().__init__(client=None)  # We do not use a generic OpenBankingClient
        self._svc: MizrahiBankAuthService = service

        # plug‑in concrete managers
        self.oauth2: MizrahiOAuth2Manager = MizrahiOAuth2Manager(self)

    def refresh_access_token(self) -> TokenResponse:
        """Retrieves the refresh token for the Mizrahi Bank API."""
        return self.oauth2.refresh_access_token()

    # Expose the raw service for internal helpers ---------------------------------
    @property
    def svc(self) -> MizrahiBankAuthService:
        return self._svc
