from typing import TYPE_CHECKING

from israel_open_banking.core.ais.savings_and_loans.base import AISLoansAccountManager
from israel_open_banking.core.ais.savings_and_loans.exceptions import AISAccountSavingsAndLoansException
from israel_open_banking.core.ais.savings_and_loans.models import AccountDetailsSavingsLoans, \
    LoanAccountList
from israel_open_banking.core.exceptions import raise_from_response

if TYPE_CHECKING:
    from israel_open_banking.psd2_savings_and_loans.loans.isracard.clients.isracard_loans_ais_client import \
        IsracardAISLoansClient


class IsracardLoansAccountManager(AISLoansAccountManager):
    def __init__(self, ais_client: "IsracardAISLoansClient") -> None:
        super().__init__(ais_client)
        self.ais_client: "IsracardAISLoansClient" = ais_client

    def get_accounts(self) -> LoanAccountList:
        resp = self.ais_client.svc.get_accounts()
        if resp.status_code >= 400:
            raise_from_response(resp, AISAccountSavingsAndLoansException)
        return LoanAccountList.model_validate_json(resp.text)

    def get_account_details(
            self, loan_account_id: str
    ) -> AccountDetailsSavingsLoans:
        resp = self.ais_client.svc.get_account_details(loan_account_id)
        if resp.status_code >= 400:
            raise_from_response(resp, AISAccountSavingsAndLoansException)
        return AccountDetailsSavingsLoans.model_validate(resp.json()["loanAccount"])
