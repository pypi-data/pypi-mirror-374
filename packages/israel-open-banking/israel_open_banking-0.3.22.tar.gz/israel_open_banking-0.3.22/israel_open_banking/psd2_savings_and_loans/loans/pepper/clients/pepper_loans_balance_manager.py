from __future__ import annotations

from typing import TYPE_CHECKING

from israel_open_banking.core.ais.savings_and_loans.base import AISLoansBalanceManager
from israel_open_banking.core.ais.savings_and_loans.exceptions import AISBalanceSavingsAndLoansException
from israel_open_banking.core.ais.savings_and_loans.models import LoanBalanceList
from israel_open_banking.core.exceptions import raise_from_response

if TYPE_CHECKING:
    from israel_open_banking.psd2_savings_and_loans.loans.pepper.clients.pepper_loans_ais_client import \
        PepperAISLoansClient


class PepperLoansBalanceManager(AISLoansBalanceManager):
    """Handles /accounts/{id}/balances endpoints for Pepper-Bank."""

    def __init__(self, ais_client: PepperAISLoansClient) -> None:
        super().__init__(ais_client)
        self.ais_client: PepperAISLoansClient = ais_client

    # --------------------------------------------------------------------- #

    def get_balances(self, loan_account_id: str) -> LoanBalanceList:
        resp = self.ais_client.svc.get_balances(loan_account_id)
        if resp.status_code >= 400:
            raise_from_response(resp, AISBalanceSavingsAndLoansException)
        return LoanBalanceList.model_validate_json(resp.text)
