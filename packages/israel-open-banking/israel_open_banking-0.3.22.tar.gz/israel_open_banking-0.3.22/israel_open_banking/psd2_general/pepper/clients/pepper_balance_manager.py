from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING

from israel_open_banking.core.ais import AISBalanceManager, BalanceList
from israel_open_banking.core.ais.general.exceptions import AISBalanceException
from israel_open_banking.core.exceptions import raise_from_response

if TYPE_CHECKING:
    from israel_open_banking.psd2_general.pepper.clients.pepper_ais_client import PepperAISClient


class PepperBalanceManager(AISBalanceManager):
    """Handles /accounts/{id}/balances endpoints for Pepper-Bank."""

    def __init__(self, ais_client: PepperAISClient) -> None:
        super().__init__(ais_client)
        self.ais_client: PepperAISClient = ais_client

    # --------------------------------------------------------------------- #

    def get_balances(self, account_id: str) -> BalanceList:
        resp = self.ais_client.svc.get_account_balances(account_id)
        if resp.status_code >= 400:
            raise_from_response(resp, AISBalanceException)
        return BalanceList.model_validate_json(resp.text)
