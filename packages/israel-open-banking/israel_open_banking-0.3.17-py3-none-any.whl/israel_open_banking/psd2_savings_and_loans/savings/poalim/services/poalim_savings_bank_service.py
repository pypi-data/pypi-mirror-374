from __future__ import annotations

from datetime import date
from typing import Optional
from urllib.parse import urlencode

import requests

from israel_open_banking.config import get_config
from israel_open_banking.core.ais.general.enums import Aspsp

config = get_config()

from israel_open_banking.core.ais import BookingStatus

from israel_open_banking.core.api_endpoints import SAVINGS_ACCOUNTS_ENDPOINT, \
    SAVINGS_ACCOUNT_BY_ID_ENDPOINT, SAVINGS_ACCOUNT_BALANCES_ENDPOINT, SAVINGS_ACCOUNT_TRANSACTIONS_ENDPOINT
from israel_open_banking.core.bank_url_builder import BankUrlBuilder

from israel_open_banking.core.headers import build_headers
from israel_open_banking.core.ssl_adapter import send_get_request


class PoalimBankSavingsService:
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

        self.ca_cert = config.POALIM_CA_CERT_PATH
        self.url_builder = BankUrlBuilder(
            api_base_url=config.POALIM_SAVINGS_AND_LOANS_API_URL
        )

    def get_accounts(self) -> requests.Response:
        return self._signed_get(SAVINGS_ACCOUNTS_ENDPOINT)

    def get_account_details(self, savings_account_id: str) -> requests.Response:
        endpoint = SAVINGS_ACCOUNT_BY_ID_ENDPOINT.format(savings_account_id=savings_account_id)
        return self._signed_get(endpoint)

    def get_balances(self, savings_account_id: str) -> requests.Response:
        endpoint = SAVINGS_ACCOUNT_BALANCES_ENDPOINT.format(savings_account_id=savings_account_id)
        return self._signed_get(endpoint)

    def get_transactions(
            self,
            savings_account_id: str,
            date_from: date,
            booking_status: BookingStatus,
            date_to: Optional[date] = None,
            entry_reference_from: str | None = None,
            delta_list: bool = False,
    ) -> requests.Response:
        params = {
            "dateFrom": date_from.isoformat() if date_from else "",
            "dateTo": date_to.isoformat() if date_to else "",
            "bookingStatus": booking_status.value if booking_status else "",
            "entryReferenceFrom": entry_reference_from,
            "deltaList": str(delta_list).lower() if delta_list else "",
        }

        endpoint = SAVINGS_ACCOUNT_TRANSACTIONS_ENDPOINT.format(savings_account_id=savings_account_id)
        return self._signed_get(endpoint, params)

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
        headers, _ = build_headers(Aspsp.POALIM,
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
