from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Optional

from israel_open_banking.core.ais import BookingStatus
from israel_open_banking.core.ais.savings_and_loans import AISTransactionSavingsAndLoansException
from israel_open_banking.core.ais.savings_and_loans.base import AISLoansTransactionManager
from israel_open_banking.core.ais.savings_and_loans.models import LoanAccountTransactionReport
from israel_open_banking.core.exceptions import raise_from_response

if TYPE_CHECKING:
    from israel_open_banking.psd2_savings_and_loans.loans.max.clients.max_loans_ais_client import \
        MaxAISLoansClient


class MaxLoansTransactionManager(AISLoansTransactionManager):
    def __init__(self, ais_client: MaxAISLoansClient) -> None:  # noqa: D401
        super().__init__(ais_client)
        self.ais_client: MaxAISLoansClient = ais_client

    def get_transactions(
            self,
            loan_account_id: str,
            date_from: date,
            booking_status: BookingStatus,
            date_to: Optional[date] = None,
            entry_reference_from: str | None = None,
            delta_list: bool = False,
    ) -> LoanAccountTransactionReport:
        resp = self.ais_client.svc.get_transactions(
            loan_account_id,
            date_from,
            booking_status,
            date_to,
            entry_reference_from,
            delta_list,
        )
        if resp.status_code >= 400:
            raise_from_response(resp, AISTransactionSavingsAndLoansException)
        return LoanAccountTransactionReport.model_validate_json(resp.text)
