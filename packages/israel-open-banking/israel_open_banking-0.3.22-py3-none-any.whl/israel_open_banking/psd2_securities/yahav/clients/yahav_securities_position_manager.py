from __future__ import annotations

from typing import TYPE_CHECKING

from israel_open_banking.core.ais.securities.base import AISSecuritiesPositionManager
from israel_open_banking.core.ais.securities.exceptions import AISPositionSecuritiesException
from israel_open_banking.core.ais.securities.models import SecuritiesAccountPositionsWrapper
from israel_open_banking.core.exceptions import raise_from_response

if TYPE_CHECKING:
    from israel_open_banking.psd2_securities.yahav.clients.yahav_securities_ais_client import \
        YahavAISSecuritiesClient


class YahavSecuritiesPositionManager(AISSecuritiesPositionManager):
    """Handles /securities-accounts/{id}/positions endpoints for Yahav-Bank."""

    def __init__(self, ais_client: YahavAISSecuritiesClient) -> None:
        super().__init__(ais_client)
        self.ais_client: YahavAISSecuritiesClient = ais_client

    def get_positions(self, securities_account_id: str) -> SecuritiesAccountPositionsWrapper:
        resp = self.ais_client.svc.get_positions(securities_account_id)
        if resp.status_code >= 400:
            raise_from_response(resp, AISPositionSecuritiesException)
        return SecuritiesAccountPositionsWrapper.model_validate_json(resp.text)
