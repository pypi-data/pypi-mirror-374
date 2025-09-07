from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Optional

from israel_open_banking.core.ais.securities.base import AISSecuritiesOrderManager
from israel_open_banking.core.ais.securities.enums import OrderStatusCode
from israel_open_banking.core.ais.securities.exceptions import AISOrderSecuritiesException
from israel_open_banking.core.ais.securities.models import SecuritiesOrdersWrapper, SecuritiesOrder
from israel_open_banking.core.exceptions import raise_from_response

if TYPE_CHECKING:
    from israel_open_banking.psd2_securities.yahav.clients.yahav_securities_ais_client import \
        YahavAISSecuritiesClient


class YahavSecuritiesOrderManager(AISSecuritiesOrderManager):
    """Handles /securities-accounts/{id}/positions endpoints for Yahav-Bank."""

    def __init__(self, ais_client: YahavAISSecuritiesClient) -> None:
        super().__init__(ais_client)
        self.ais_client: YahavAISSecuritiesClient = ais_client

    def get_orders(self, securities_account_id: str,
                   date_from: date,
                   date_to: Optional[date] = None,
                   order_status: Optional[OrderStatusCode] = None
                   ) -> SecuritiesOrdersWrapper:
        resp = self.ais_client.svc.get_orders(
            securities_account_id,
            date_from,
            date_to,
            order_status
        )
        if resp.status_code >= 400:
            raise_from_response(resp, AISOrderSecuritiesException)
        return SecuritiesOrdersWrapper.model_validate_json(resp.text)

    def get_order_details(
            self, securities_account_id: str, order_id: str
    ) -> SecuritiesOrder:
        resp = self.ais_client.svc.get_order_details(securities_account_id, order_id)
        if resp.status_code >= 400:
            raise_from_response(resp, AISOrderSecuritiesException)
        return SecuritiesOrder.model_validate_json(resp.text)
