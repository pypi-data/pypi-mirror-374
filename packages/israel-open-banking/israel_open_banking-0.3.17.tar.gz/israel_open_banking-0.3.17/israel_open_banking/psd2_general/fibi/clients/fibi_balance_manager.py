from __future__ import annotations

from typing import TYPE_CHECKING

from israel_open_banking.core.ais import AISBalanceManager, BalanceList
from israel_open_banking.core.ais.general.exceptions import AISBalanceException
from israel_open_banking.core.exceptions import raise_from_response

if TYPE_CHECKING:
    from israel_open_banking.psd2_general.fibi.clients.fibi_ais_client import FibiAISClient


class FibiBalanceManager(AISBalanceManager):
    """Handles /accounts/{id}/balances endpoints for Fibi-Bank."""

    def __init__(self, ais_client: FibiAISClient) -> None:
        super().__init__(ais_client)
        self.ais_client: FibiAISClient = ais_client

    # --------------------------------------------------------------------- #

    def get_balances(self, account_id: str) -> BalanceList:
        resp = self.ais_client.svc.get_account_balances(account_id)
        if resp.status_code >= 400:
            raise_from_response(resp, AISBalanceException)
        return BalanceList.model_validate_json(resp.text)
