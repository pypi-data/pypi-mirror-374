
from typing import TYPE_CHECKING

from israel_open_banking.core.ais import (
    AccountDetails,
    AccountList,
    AISAccountException,
    AISAccountManager,
)
from israel_open_banking.core.ais.general.exceptions import AISAccountNotFoundException
from israel_open_banking.core.exceptions import raise_from_response

if TYPE_CHECKING:
    from israel_open_banking.psd2_general.fibi.clients.fibi_ais_client import FibiAISClient


class FibiAccountManager(AISAccountManager):
    def __init__(self, ais_client: "FibiAISClient") -> None:
        super().__init__(ais_client)
        self.ais_client: "FibiAISClient" = ais_client

    def get_accounts(self, with_balance: bool = False) -> AccountList:
        resp = self.ais_client.svc.get_accounts(with_balance)
        if resp.status_code >= 400:
            raise_from_response(resp, AISAccountException)
        return AccountList.model_validate_json(resp.text)

    def get_account_details(self, account_id: str, with_balance: bool = False) -> AccountDetails:
        resp = self.ais_client.svc.get_account_by_id(account_id, with_balance)
        if resp.status_code == 404:
            raise AISAccountNotFoundException(account_id, status_code=404)
        if resp.status_code >= 400:
            raise_from_response(resp, AISAccountException)
        return AccountDetails.model_validate(resp.json()["account"])
