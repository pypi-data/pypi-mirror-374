from typing import TYPE_CHECKING

from israel_open_banking.core.ais.savings_and_loans.base import AISSavingsAccountManager
from israel_open_banking.core.ais.savings_and_loans.exceptions import AISAccountSavingsAndLoansException
from israel_open_banking.core.ais.savings_and_loans.models import SavingAccountList, AccountDetailsSavingsLoans
from israel_open_banking.core.exceptions import raise_from_response

if TYPE_CHECKING:
    from israel_open_banking.psd2_savings_and_loans.savings.yahav.clients.yahav_savings_ais_client import \
        YahavAISSavingsClient


class YahavSavingsAccountManager(AISSavingsAccountManager):
    def __init__(self, ais_client: "YahavAISSavingsClient") -> None:
        super().__init__(ais_client)
        self.ais_client: "YahavAISSavingsClient" = ais_client

    def get_accounts(self) -> SavingAccountList:
        resp = self.ais_client.svc.get_accounts()
        if resp.status_code >= 400:
            raise_from_response(resp, AISAccountSavingsAndLoansException)
        return SavingAccountList.model_validate_json(resp.text)

    def get_account_details(
            self, savings_account_id: str
    ) -> AccountDetailsSavingsLoans:
        resp = self.ais_client.svc.get_account_details(savings_account_id)
        if resp.status_code >= 400:
            raise_from_response(resp, AISAccountSavingsAndLoansException)
        return AccountDetailsSavingsLoans.model_validate(resp.json()["savingsAccount"])
