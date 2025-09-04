from __future__ import annotations

from typing import TYPE_CHECKING

from israel_open_banking.core.ais.savings_and_loans import AISSavingsBalanceManager
from israel_open_banking.core.ais.savings_and_loans.exceptions import AISBalanceSavingsAndLoansException
from israel_open_banking.core.ais.savings_and_loans.models import SavingBalanceList, LoanBalanceList
from israel_open_banking.core.exceptions import raise_from_response

if TYPE_CHECKING:
    from israel_open_banking.psd2_savings_and_loans.savings.poalim.clients.poalim_savings_ais_client import PoalimAISSavingsClient


class PoalimSavingsBalanceManager(AISSavingsBalanceManager):
    """Handles /accounts/{id}/balances endpoints for Poalim-Bank."""

    def __init__(self, ais_client: PoalimAISSavingsClient) -> None:
        super().__init__(ais_client)
        self.ais_client: PoalimAISSavingsClient = ais_client

    # --------------------------------------------------------------------- #

    def get_balances(self, saving_account_id: str) -> SavingBalanceList:
        resp = self.ais_client.svc.get_balances(saving_account_id)
        if resp.status_code >= 400:
            raise_from_response(resp, AISBalanceSavingsAndLoansException)
        return SavingBalanceList.model_validate_json(resp.text)
