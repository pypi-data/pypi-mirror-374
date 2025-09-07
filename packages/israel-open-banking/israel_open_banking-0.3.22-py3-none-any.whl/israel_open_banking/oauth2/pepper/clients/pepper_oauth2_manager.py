from __future__ import annotations

from typing import TYPE_CHECKING

from israel_open_banking.core.exceptions import raise_from_response
from israel_open_banking.core.oauth.base import OAuth2Manager
from israel_open_banking.core.oauth.exceptions import AISAuthorizationException
from israel_open_banking.core.oauth.models import TokenResponse

if TYPE_CHECKING:
    from israel_open_banking.oauth2.pepper.clients.pepper_oauth2_client import PepperOAuth2Client


class PepperOAuth2Manager(OAuth2Manager):
    def __init__(self, client: PepperOAuth2Client) -> None:  # noqa: D401
        super().__init__(client)
        self.client: PepperOAuth2Client = client

    def get_access_token(self) -> str:
        """
        Retrieves the access token for the Pepper Bank API.

        Returns:
            str: The access token.
        """
        pass

    def refresh_access_token(self) -> TokenResponse:
        """
        Retrieves the refresh token for the Pepper Bank API.

        Returns:
            str: The refresh token.
        """
        resp = self.client.svc.refresh_access_token()
        if resp.status_code >= 400:
            raise_from_response(resp, AISAuthorizationException)
        return TokenResponse.model_validate_json(resp.text)
