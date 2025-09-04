from typing import TYPE_CHECKING, Optional

from israel_open_banking.core.ais.securities.base import AISSecuritiesAccountManager
from israel_open_banking.core.ais.securities.exceptions import AISAccountSecuritiesException
from israel_open_banking.core.ais.securities.models import SecuritiesAccountList, SecuritiesAccountDetails
from israel_open_banking.core.exceptions import raise_from_response

if TYPE_CHECKING:
    from israel_open_banking.psd2_securities.pepper.clients.pepper_securities_ais_client import \
        PepperAISSecuritiesClient


class PepperSecuritiesAccountManager(AISSecuritiesAccountManager):
    def __init__(self, ais_client: "PepperAISSecuritiesClient") -> None:
        super().__init__(ais_client)
        self.ais_client: "PepperAISSecuritiesClient" = ais_client

    def get_accounts(self, evaluation_currency: Optional[str] = None) -> SecuritiesAccountList:
        resp = self.ais_client.svc.get_accounts(evaluation_currency)
        if resp.status_code >= 400:
            raise_from_response(resp, AISAccountSecuritiesException)
        return SecuritiesAccountList.model_validate_json(resp.text)

    def get_account_details(
            self, securities_account_id: str,
            evaluation_currency: Optional[str] = None
    ) -> SecuritiesAccountDetails:
        resp = self.ais_client.svc.get_account_details(securities_account_id, evaluation_currency)
        if resp.status_code >= 400:
            raise_from_response(resp, AISAccountSecuritiesException)
        return SecuritiesAccountDetails.model_validate(resp.json()["securitiesAccount"])
