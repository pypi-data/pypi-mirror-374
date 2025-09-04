from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Optional

from israel_open_banking.core.ais import AISTransactionManager, BookingStatus, AISTransactionException, \
    TransactionDetails
from israel_open_banking.core.ais.general.models import AccountTransactionReport
from israel_open_banking.core.exceptions import raise_from_response

if TYPE_CHECKING:
    from israel_open_banking.psd2_general.yahav.clients.yahav_ais_client import YahavAISClient


class YahavTransactionManager(AISTransactionManager):
    def __init__(self, ais_client: YahavAISClient) -> None:  # noqa: D401
        super().__init__(ais_client)
        self.ais_client: YahavAISClient = ais_client

    def get_transactions(
            self,
            account_id: str,
            date_from: date,
            booking_status: BookingStatus,
            date_to: Optional[date] = None,
            with_balance: bool = False,
            entry_reference_from: Optional[str] = None,
            delta_list: bool = False,
    ) -> AccountTransactionReport:  # noqa: D401
        resp = self.ais_client.svc.get_account_transactions(account_id,
                                                            date_from,
                                                            booking_status,
                                                            date_to,
                                                            with_balance,
                                                            entry_reference_from,
                                                            delta_list, )
        if resp.status_code >= 400:
            raise_from_response(resp, AISTransactionException)
        return AccountTransactionReport.model_validate_json(resp.text)

    def get_transaction_details(self, account_id: str, transaction_id: str) -> TransactionDetails:  # noqa: D401
        resp = self.ais_client.svc.get_transaction_details(account_id, transaction_id)
        if resp.status_code >= 400:
            raise_from_response(resp, AISTransactionException)
        return TransactionDetails.model_validate_json(resp.text)
