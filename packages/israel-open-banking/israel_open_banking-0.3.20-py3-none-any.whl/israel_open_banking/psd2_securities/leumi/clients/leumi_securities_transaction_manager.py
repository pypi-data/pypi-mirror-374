from __future__ import annotations

import json
from datetime import date
from typing import TYPE_CHECKING, Optional

from israel_open_banking.core.ais.securities.base import AISSecuritiesTransactionManager
from israel_open_banking.core.ais.securities.exceptions import AISTransactionSecuritiesException
from israel_open_banking.core.ais.securities.models import SecuritiesTransactionsWrapper, SecuritiesTransaction
from israel_open_banking.core.exceptions import raise_from_response

if TYPE_CHECKING:
    from israel_open_banking.psd2_securities.leumi.clients.leumi_securities_ais_client import \
        LeumiAISSecuritiesClient


class LeumiSecuritiesTransactionManager(AISSecuritiesTransactionManager):
    def __init__(self, ais_client: LeumiAISSecuritiesClient) -> None:  # noqa: D401
        super().__init__(ais_client)
        self.ais_client: LeumiAISSecuritiesClient = ais_client

    def get_transactions(
            self,
            securities_account_id: str,
            date_from: date,
            date_to: Optional[date] = None,
            entry_reference_from: Optional[str] = None,
            delta_list: bool = False,
    ) -> SecuritiesTransactionsWrapper:
        resp = self.ais_client.svc.get_transactions(
            securities_account_id,
            date_from,
            date_to,
            entry_reference_from,
            delta_list,
        )
        if resp.status_code >= 400:
            raise_from_response(resp, AISTransactionSecuritiesException)

        # TODO: Remove this once the API is fixed
        data = json.loads(resp.text)
        if "securitiesAccounts" in data:
            data["securitiesAccount"] = data.pop("securitiesAccounts")
        return SecuritiesTransactionsWrapper.model_validate(data)
        # return SecuritiesTransactionsWrapper.model_validate_json(resp.text)

    def get_transaction_details(
            self, securities_account_id: str, transaction_id: str
    ) -> SecuritiesTransaction:
        resp = self.ais_client.svc.get_transaction_details(securities_account_id, transaction_id)
        if resp.status_code >= 400:
            raise_from_response(resp, AISTransactionSecuritiesException)
        return SecuritiesTransaction.model_validate_json(resp.text)
