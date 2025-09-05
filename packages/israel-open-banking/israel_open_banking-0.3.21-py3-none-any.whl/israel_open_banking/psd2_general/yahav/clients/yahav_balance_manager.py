from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING

from israel_open_banking.core.ais import AISBalanceManager, BalanceList
from israel_open_banking.core.ais.general.exceptions import AISBalanceException
from israel_open_banking.core.exceptions import raise_from_response

if TYPE_CHECKING:
    from israel_open_banking.psd2_general.yahav.clients.yahav_ais_client import YahavAISClient


class YahavBalanceManager(AISBalanceManager):
    """Handles /accounts/{id}/balances endpoints for Yahav-Bank."""

    def __init__(self, ais_client: YahavAISClient) -> None:
        super().__init__(ais_client)
        self.ais_client: YahavAISClient = ais_client

    # --------------------------------------------------------------------- #

    def get_balances(self, account_id: str) -> BalanceList:
        resp = self.ais_client.svc.get_account_balances(account_id)
        if resp.status_code >= 400:
            raise_from_response(resp, AISBalanceException)
        # TODO: Remove this once the API is fixed
        data = json.loads(resp.text)
        for balance in data.get("balances", []):
            # Convert referenceDate from MM-DD-YYYY to ISO
            ref_date = balance.get("referenceDate")
            if ref_date:
                try:
                    parsed_date = datetime.strptime(ref_date, "%m-%d-%Y")
                    balance["referenceDate"] = parsed_date.strftime("%Y-%m-%d")
                except ValueError:
                    pass  # Keep original if format is invalid

            # Rename creditLimitIcluded → creditLimitIncluded
            if "creditLimitIcluded" in balance:
                balance["creditLimitIncluded"] = balance.pop("creditLimitIcluded")

        return BalanceList.model_validate(data)
        # return BalanceList.model_validate_json(data)
