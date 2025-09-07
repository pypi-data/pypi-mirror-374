# def main():
#     print("Running Open Banking SDK")
import datetime
from pathlib import Path

from dotenv import load_dotenv



ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env", override=True)  # ← 1️⃣ FIRST: load env vars

# Only now is it safe to import modules that read `config`

from israel_open_banking.psd2_general.discount.clients.discount_ais_client import DiscountAISClient
from israel_open_banking.psd2_general.discount.services.discount_bank_service import DiscountBankService
from israel_open_banking.psd2_securities.discount.clients.discount_securities_ais_client import \
    DiscountAISSecuritiesClient
from israel_open_banking.oauth2.discount.clients.discount_oauth2_client import DiscountOAuth2Client
from israel_open_banking.oauth2.discount.services.discount_bank_auth_service import DiscountBankAuthService
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

        svc = DiscountBankService(
            consent_id='78200',
            access_token="AAIaT0JfSUwtSVNBLTUxNjU4ODI2Ni1TaGF2dmVM0yy054Dy71uG6XN9_wL4UVG0pNnf7cZ-Q97qF4R8hwELz6kfLLUCabkil8C06tKoe_j6wJKdhU60T7a8BDFb4QAbJScbMr9kYfZyFe8j6MOxbtGsfaBJ8fK7oVcoHEcztzH3CedUu-Vj0ucWXOQmJr6mUua6U8GYm53sHkF1kvnEbIsNb9DWIYH_zIA7DBB5aQkZxtyO67j2dqhDT-CDXqZnabdEN84b1Nsfzub3tZX-alegbQ9ygkXjUBaIovpmQ0Wjyijzu0LIkn7d0gy0UZrRjfpP6dxp0lwqnW6KNz_dKcSYpYV9ayFXTRv1c0eCBpbDpDZ1eYUTErgzxVey6Yo7KSa5gbScxbYglDSzxaNw_QhbBC0Pd6kaW1sSsSCp7MrzOEJtRkn56kPfn5Vuo5SOPQmGcPLbK2yh7x-3OOguPinDEJG2ErVkpcER7dETVlfRWZWICsCyAdDk7pWuN1C_zFlNHduNfCD-Ty-LChRif9H97tRfKJAKS80P_U0s31sUIZFL9R3VJ1gpuY1VJPCogi2BAT9t7sCPZrZZlgDcIbLzjh3uMwVDDrsdIoGHaehdEtTHKVU9pQ_P_mPAt-CqVQLq0Ivi_e_40fJh3jN-QIO1F1NkIuDORgqUiotznl9ThEnk-hHTu8F1Nl4LmfE6qseMop6-FGBU8jYDyP6Hox0ouRuUG2XD8giHJsk",
            psu_id="222210007",
        )
        client = DiscountAISClient(svc)

        refresh_token = DiscountBankAuthService(
            refresh_token="AALluewqQEIEpwhZwK63El0CmsfIwFaU3PR0y_udl9Io9o9xhdgiw8Wqjuiug2F9cWqF5sa2Q6XzN8DTV4xVFhhzKLPPw_XprczZZde3TmMMwR5RFN3vUX_hvsnfPjVCJdypvm1MS9zl90m_j1olU7DKh17FedKORC9hY9i7dxXGmcVoiJxv-j3sCMZfTA-tl4ZrqxlfJ-8ekKH8T-jiU7e74Cyc5ryM-w8eyK9Tw_h0o5XD1QqECKuTcx1DiI8Ow_WSUeJJoVvMosGyREFuwAk5yNp9mpwVqKuhZZCr2uwxOMAMKUJ30TlRwEyvKG-9yHRnaIYozyfDpMJ5ajpLUSnt1Yguq4pIBjS3K8b2jSTkjdUWOGxQRDMO3jLw2wkuhl65cIhfMgOcy3ADPVYWsXpw6CG6taOxZfYRLhRMdM8JR0Q5SdKTdWwo2RCO5C6z1YYWUZhmOf_l7HQT8LafL0NCRY9gArep5elsFFwE1-9oXhtpJq1Klxq1QjWv-8mn75SdemgalK0tgIhAOkXmv9_ZqxSICzN7UwvaO-ACzXt5ziVa8T8E4uVXjGie2utvlPidG95Zh-TRQeocAFnN88iSjSiIbF7RXb-OopxrZufl7CUe-qVJrsnD7LUq6v6r-8CoD-9xy2HcAjVrnYBxpzDOpoFDvLdORYGjH0zEDaDGY2Jq2njbWkgp1zwFIwWj-v1nHdc0Y5W9cgSkYU_WMe--",
            token_endpoint="https://mtls-api-nonprod.discountbank.co.il/devapi/cert/psd2/v1.0.6/consent/token")
        auth_client = DiscountOAuth2Client(refresh_token)

        # svc = BitService(
        #     consent_id='192',
        #     access_token='eyJhbGciOiJSUzI1NiJ9.eyJjbmYiOnsieDV0I1MyNTYiOiJZalUxT0RjMU1qWXlPV00zTmpZMVpEWTVNamxsTUdJeE9XVXpObUl6T0dObE16azRNVEppWlRSbFlqY3haVEF3WlRnME1qQTROVEE0TmpBM1pHUXpZZyJ9LCJpc3MiOiJodHRwczovL29wZW4tYmFua2luZy5iaXRwYXkuY28uaWwiLCJpYXQiOjE3NTYwMjc0MzUsImF1ZCI6Ik9COklMLUlTQS01MTY1ODgyNjYtU2hhdnZlIiwianRpIjoiNDM5ODU1ZDAtZTYzZi00N2NmLWE2ZGMtZWJhM2M2NmUxODQzIiwic3ViIjoxOTIsInNjcCI6IlBTUF9BSSJ9.evBSXe5ueC7MmhgWn-beknl_mGZpXdgn2mAlasXTuewMcvT1ulzxCN77_uNP6gSN6zPi-HcBnc-Rgu0J06lfAuI8l8qaH2g1avdJsu9Kds8Y0I6UoVc2NlJlx8-nVAiW7cpPnlzzvV3lKuFRuvsteasjJFMnhdSoVG9NZO76WfaVjYnEAtQ0A0eRn6CGBp_njX5ugWi7jP9saIF5e1li43uZ34GtS9VXItxdNQEZ0pTAfYqLL858eOUEIoTjxsvZy6CglmCB1bjz0PNWC0AMQHrdBdwIXChO4tA8v4IIS0SZE0tTG05G3gSxndYr69LrlzJYs7zRD17VvPsxUl5KqQ',
        #     psu_id='336136163'
        # )
        #
        # client = BitAISClient(svc)

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
