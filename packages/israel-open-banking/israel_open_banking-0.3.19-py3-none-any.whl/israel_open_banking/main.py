# def main():
#     print("Running Open Banking SDK")
import datetime
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env", override=True)  # ← 1️⃣ FIRST: load env vars

# Only now is it safe to import modules that read `config`

from israel_open_banking.psd2_securities.fibi.clients.fibi_securities_ais_client import FibiAISSecuritiesClient
from israel_open_banking.psd2_securities.fibi.services.fibi_securities_bank_service import FibiBankSecuritiesService
from israel_open_banking.core.ais.general.enums import Aspsp
from israel_open_banking.psd2_general.fibi.clients.fibi_ais_client import FibiAISClient
from israel_open_banking.psd2_general.fibi.services.fibi_bank_service import FibiBankService
from israel_open_banking.oauth2.fibi.clients.fibi_oauth2_client import FibiOAuth2Client
from israel_open_banking.oauth2.fibi.services.fibi_bank_auth_service import FibiBankAuthService
from israel_open_banking.psd2_general.bit.clients.bit_ais_client import BitAISClient
from israel_open_banking.psd2_general.bit.services.bit_service import BitService
from israel_open_banking.config import get_config
from israel_open_banking.psd2_securities.poalim.clients.poalim_securities_ais_client import PoalimAISSecuritiesClient
from israel_open_banking.psd2_securities.poalim.services.poalim_securities_bank_service import \
    PoalimBankSecuritiesService

from israel_open_banking.oauth2.poalim.clients.poalim_oauth2_client import PoalimOAuth2Client
from israel_open_banking.oauth2.poalim.services.poalim_bank_auth_service import PoalimBankAuthService


config = get_config()

print("DISCOUNT_API_URL =", config.DISCOUNT_API_URL)

if __name__ == "__main__":
    try:

        # svc = PoalimBankSecuritiesService(
        #     consent_id='24d7398b-545d-4bda-db11-2a00bd625201',
        #     access_token="GvMNfEh4A7msfddjg1oAcfjvuGy2",
        #     psu_id="100100106",
        # )
        # client = PoalimAISSecuritiesClient(svc)
        #
        # refresh_token = PoalimBankAuthService(
        #     refresh_token="NxNTwXMlY4jPv880aSVuGFp9FCjHE9JT",
        #     token_endpoint="https://openbankingsb.poalim-api.co.il/xs2a/unpr/oauth2/v1/token")
        # auth_client = PoalimOAuth2Client(refresh_token)

        svc = BitService(
            consent_id='192',
            access_token='eyJhbGciOiJSUzI1NiJ9.eyJjbmYiOnsieDV0I1MyNTYiOiJZalUxT0RjMU1qWXlPV00zTmpZMVpEWTVNamxsTUdJeE9XVXpObUl6T0dObE16azRNVEppWlRSbFlqY3haVEF3WlRnME1qQTROVEE0TmpBM1pHUXpZZyJ9LCJpc3MiOiJodHRwczovL29wZW4tYmFua2luZy5iaXRwYXkuY28uaWwiLCJpYXQiOjE3NTYwMjc0MzUsImF1ZCI6Ik9COklMLUlTQS01MTY1ODgyNjYtU2hhdnZlIiwianRpIjoiNDM5ODU1ZDAtZTYzZi00N2NmLWE2ZGMtZWJhM2M2NmUxODQzIiwic3ViIjoxOTIsInNjcCI6IlBTUF9BSSJ9.evBSXe5ueC7MmhgWn-beknl_mGZpXdgn2mAlasXTuewMcvT1ulzxCN77_uNP6gSN6zPi-HcBnc-Rgu0J06lfAuI8l8qaH2g1avdJsu9Kds8Y0I6UoVc2NlJlx8-nVAiW7cpPnlzzvV3lKuFRuvsteasjJFMnhdSoVG9NZO76WfaVjYnEAtQ0A0eRn6CGBp_njX5ugWi7jP9saIF5e1li43uZ34GtS9VXItxdNQEZ0pTAfYqLL858eOUEIoTjxsvZy6CglmCB1bjz0PNWC0AMQHrdBdwIXChO4tA8v4IIS0SZE0tTG05G3gSxndYr69LrlzJYs7zRD17VvPsxUl5KqQ',
            psu_id='336136163'
        )

        client = BitAISClient(svc)

        # loans_service = MaxLoansService(
        #     consent_id='bcc97297369fd16dcbfaeb91',
        #     access_token="AAIZb2JpbC1pc2EtNTE2NTg4MjY2LXNoYXZ2ZeIXV1BjTTEsV-fdwKNaSIFYIoQscxzmnfmko-29uLDGgUEm9OfVlFm1FU5CTmKJYjqFkDyeW2E4tlzQSPDIAfGZJ0z5r1IqG7hh5x28DrATYgoJbi8hF6pig_22aW_IrCzTQPdHfkMXnfLz7YMnLoE",
        #     psu_id="111111111")
        # loans_client = MaxAISLoansClient(loans_service)

        # resp = auth_client.refresh_access_token()
        # resp = loans_client.get_transactions('3dc3d5b3-7023-4848-9853-f5400a64e81a',date_from=date(year=2025,month=5,day=2),booking_status=BookingStatus.BOOKED)

        # resp = loans_client.get_balances('3dc3d5b3-7023-4848-9853-f5400a64e81a')
        # resp = auth_client.refresh_access_token()

        try:
            # resp = client.get_orders('3B261A81F0E45B99E063020316AC441D', date_from=datetime.date(year=2025,month=1,day=2))
            # resp = client.get_order_details('securities-77776','FX_000164082610007037505020230517')
            # resp = client.get_positions('634b4a93-f448-4c80-a98f-b5c9453c28dc')
            # resp = client.get_orders('securities-77776', date_from=datetime.date(year=2024,month=1,day=2))
            # resp = client.get_transactions('securities-77776', date_from=datetime.date(year=2024,month=1,day=2))
            resp = client.get_accounts()
            # resp = auth_client.refresh_access_token()

            # print("✅ Response:", resp)
            #      print response as json
            print("✅ Response JSON:", resp.model_dump_json(indent=2))
        except Exception as e:
            print("❌ Error:", e)

        # resp = client.get_card_details('f33ff6aa-84e4-43eb-a7c2-fac6532354a0')
        # resp = client.get_transactions('f33ff6aa-84e4-43eb-a7c2-fac6532354a0',date_from=datetime.date(year=2025,month=5,day=2), booking_status=BookingStatus.PENDING)

        # resp2 = c.get_accounts()
        # #
        # print("✅ Response 2:", resp2)

        # print("✅ Response 2:", resp2)
        # resp = client.get_transaction_details('0038-0002443211','20240909163437690523TMP00701')
        # resp = client.get_savings_balances('0038-0002443211_01_152-0237-00-000377_2022-10-06')
    except Exception as e:
        print("❌ Error:", e)
