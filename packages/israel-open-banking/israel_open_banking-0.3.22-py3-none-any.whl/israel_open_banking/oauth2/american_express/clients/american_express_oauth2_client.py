from __future__ import annotations

from israel_open_banking.core.oauth.base import OAuth2BaseClient
from israel_open_banking.core.oauth.models import TokenResponse
from israel_open_banking.oauth2.american_express.clients.american_express_oauth2_manager import AmericanExpressOAuth2Manager
from israel_open_banking.oauth2.american_express.services.american_express_auth_service import AmericanExpressAuthService

"""AmericanExpress‑Bank concrete implementation of the PSD2 AIS abstraction layer.

This file wires the bank‑specific HTTP wrapper (``AmericanExpressBankService``)
into the generic AIS interfaces so the rest of the application can stay
vendor‑agnostic.

All network exceptions are captured and remapped to domain‑specific AIS
exceptions defined in ``israel_open_banking.core.ais.exceptions``.
"""


class AmericanExpressOAuth2Client(OAuth2BaseClient):
    """PSD2‑compliant AIS adapter for AmericanExpress Bank."""

    def __init__(self, service: AmericanExpressAuthService) -> None:
        super().__init__(client=None)  # We do not use a generic OpenBankingClient
        self._svc: AmericanExpressAuthService = service

        # plug‑in concrete managers
        self.oauth2: AmericanExpressOAuth2Manager = AmericanExpressOAuth2Manager(self)

    def refresh_access_token(self) -> TokenResponse:
        """Retrieves the refresh token for the AmericanExpress Bank API."""
        return self.oauth2.refresh_access_token()

    # Expose the raw service for internal helpers ---------------------------------
    @property
    def svc(self) -> AmericanExpressAuthService:
        return self._svc
