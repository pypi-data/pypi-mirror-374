from __future__ import annotations

from datetime import date
from typing import Optional
from urllib.parse import urlencode

import requests

from israel_open_banking.config import get_config
from israel_open_banking.core.ais.general.enums import Aspsp
from israel_open_banking.core.ais.securities.enums import OrderStatusCode

config = get_config()

from israel_open_banking.core.api_endpoints import SECURITIES_ACCOUNTS_ENDPOINT, SECURITIES_ACCOUNT_BY_ID_ENDPOINT, \
    SECURITIES_ACCOUNT_POSITIONS_ENDPOINT, \
    SECURITIES_ACCOUNT_TRANSACTIONS_ENDPOINT, SECURITIES_ACCOUNTS_TRANSACTION_DETAILS_ENDPOINT, \
    SECURITIES_ACCOUNT_ORDERS_ENDPOINT, SECURITIES_ACCOUNTS_ORDER_DETAILS_ENDPOINT
from israel_open_banking.core.bank_url_builder import BankUrlBuilder

from israel_open_banking.core.headers import build_headers
from israel_open_banking.core.ssl_adapter import send_get_request


class MercantileBankSecuritiesService:
    def __init__(self, consent_id: str, access_token: str, psu_id: str) -> None:
        self.consent_id = consent_id
        self.access_token = access_token
        self.psu_id = psu_id

        self.qwac_cert = config.SHAVVE_QWAC_CERT_PEM_PATH
        self.qwac_key = config.SHAVVE_QWAC_KEY_PATH
        self.qwac_pw = config.SHAVVE_QWAC_KEY_PW

        self.qseal_cert = config.SHAVVE_QSEAL_CERT_PEM_PATH
        self.qseal_key = config.SHAVVE_QSEAL_KEY_PATH
        self.qseal_pw = config.SHAVVE_QSEAL_KEY_PW

        self.redirect_url = config.TPP_REDIRECT_URI

        self.ca_cert = config.MERCANTILE_CA_CERT_PATH
        self.url_builder = BankUrlBuilder(
            api_base_url=config.MERCANTILE_SECURITIES_API_URL
        )

    def get_accounts(self, evaluation_currency: Optional[str] = None) -> requests.Response:
        params = {
            "evaluationCurrency": evaluation_currency if evaluation_currency else "",
        }
        return self._signed_get(SECURITIES_ACCOUNTS_ENDPOINT, params)

    def get_account_details(self, securities_account_id: str, evaluation_currency: Optional[str] = None) -> requests.Response:
        params = {
            "evaluationCurrency": evaluation_currency if evaluation_currency else "",
        }
        endpoint = SECURITIES_ACCOUNT_BY_ID_ENDPOINT.format(securities_account_id=securities_account_id)
        return self._signed_get(endpoint, params)

    def get_positions(self, securities_account_id: str) -> requests.Response:
        endpoint = SECURITIES_ACCOUNT_POSITIONS_ENDPOINT.format(securities_account_id=securities_account_id)
        return self._signed_get(endpoint)

    def get_transactions(
            self,
            securities_account_id: str,
            date_from: date,
            date_to: Optional[date] = None,
            entry_reference_from: Optional[str] = None,
            delta_list: bool = False,
    ) -> requests.Response:
        params = {
            "dateFrom": date_from.isoformat() if date_from else "",
            "dateTo": date_to.isoformat() if date_to else "",
            "entryReferenceFrom": entry_reference_from or "",
            "deltaList": str(delta_list).lower() if delta_list else "",
        }

        endpoint = SECURITIES_ACCOUNT_TRANSACTIONS_ENDPOINT.format(securities_account_id=securities_account_id)
        return self._signed_get(endpoint, params)

    def get_transaction_details(self, securities_account_id: str, transaction_id: str) -> requests.Response:
        endpoint = SECURITIES_ACCOUNTS_TRANSACTION_DETAILS_ENDPOINT.format(securities_account_id=securities_account_id,
                                                                           transaction_id=transaction_id)
        return self._signed_get(endpoint)

    def get_orders(
            self,
            securities_account_id: str,
            date_from: date,
            date_to: Optional[date] = None,
            order_status: Optional[OrderStatusCode] = None
    ) -> requests.Response:
        params = {
            "dateFrom": date_from.isoformat() if date_from else "",
            "dateTo": date_to.isoformat() if date_to else "",
            "orderStatus": order_status.value if order_status else "",
        }
        endpoint = SECURITIES_ACCOUNT_ORDERS_ENDPOINT.format(securities_account_id=securities_account_id)
        return self._signed_get(endpoint, params)

    def get_order_details(self, securities_account_id: str, order_id: str) -> requests.Response:
        endpoint = SECURITIES_ACCOUNTS_ORDER_DETAILS_ENDPOINT.format(securities_account_id=securities_account_id,
                                                                     order_id=order_id)
        return self._signed_get(endpoint)

    def _signed_get(self, endpoint: str, params: Optional[dict] = None) -> requests.Response:
        # 1. Filter out empty values
        if params:
            filtered_params = {k: v for k, v in params.items() if v is not None and v != ""}
            query_string = f"?{urlencode(filtered_params)}" if filtered_params else ""
        else:
            query_string = ""

        # 2. Build full URL and signing path
        full_url = self.url_builder.build_url(endpoint) + query_string

        print(f"🔗 Full URL: {full_url}")

        # 3. Sign the request
        headers, _ = build_headers(Aspsp.MERCANTILE,
                                   {},
                                   extra_headers={
                                       "psu_id": self.psu_id,
                                       "tpp-redirect-uri": self.redirect_url,
                                       "access_token": self.access_token,
                                       "consent_id": self.consent_id,
                                       "psu_ip": '127.0.0.1',
                                   })

        # ✅ 4. Send GET request
        return send_get_request(
            full_url,
            headers,
            self.qwac_cert,
            self.qwac_key,
            self.qwac_pw,
            self.ca_cert
        )
