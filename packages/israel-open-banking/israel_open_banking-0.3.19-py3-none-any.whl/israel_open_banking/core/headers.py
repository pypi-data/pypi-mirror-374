import base64
import hashlib
import json
import re
import urllib.parse
import uuid
from dataclasses import dataclass
from email.utils import formatdate
from typing import Optional, Any

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from israel_open_banking.config import get_config
from israel_open_banking.core.ais.general.enums import Aspsp
from israel_open_banking.core.certificates import load_private_key

config = get_config()


def build_digest(body: Any) -> str:
    if body in (None, '', b'', {}):
        # No body: use hash of empty byte string
        data = b''
    else:
        # Compact JSON serialization
        data = json.dumps(body, separators=(',', ':')).encode('utf-8')

    hash_obj = hashlib.sha256(data).digest()
    return f"SHA-256={base64.b64encode(hash_obj).decode('utf-8')}"


def build_signing_string(method: str, path: str, headers: dict) -> bytes:
    return "\n".join(
        [
            f"(request-target): {method.lower()} {path}",
            f"date: {headers['date']}",
            f"digest: {headers['digest']}",
            f"x-request-id: {headers['x-request-id']}",
            f"consent-id: {headers['consent-id']}",
        ]
    ).encode()


def build_signing_string_for_consent_creation(
        method: str, path: str, headers: dict
) -> bytes:
    """
    Build signing string for POST /consents.

    Headers in signing:
    - (request-target)
    - date
    - digest
    - x-request-id
    - psu-id
    - tpp-redirect-uri
    """
    try:
        return "\n".join(
            [
                f"(request-target): {method.lower()} {path}",
                f"date: {headers['date']}",
                f"digest: {headers['digest']}",
                f"x-request-id: {headers['x-request-id']}",
                f"psu-id: {headers['psu-id']}",
                f"tpp-redirect-uri: {headers['tpp-redirect-uri']}",
            ]
        ).encode("utf-8")
    except KeyError as e:
        raise ValueError(f"Missing required header for signing: {e}")


def sign_string(signing_string: bytes, key_path: str, key_pw: str) -> str:
    private_key = load_private_key(key_path, key_pw)

    signature = private_key.sign(signing_string, padding.PKCS1v15(), hashes.SHA256())

    return base64.b64encode(signature).decode()


def build_headers(
        aspsp: Aspsp,
        body: Optional[dict[str, str]] = None,
        extra_headers: Optional[dict[str, str]] = None,
) -> tuple[dict[str, str], str]:
    # X-Request ID
    x_request_id = str(uuid.uuid4())

    # Date
    date = formatdate(timeval=None, usegmt=True)

    # Key ID
    # key_id = "SN=394E517E00D3645F04A08F1609C13FC2F1244CF9,CA=CN=Test-OpenBankingIL Seal CA, OU=GCIO-eGOV-OBCA, organizationIdentifier=NTRIL-50010037, O=Government Of Israel, C=IL"

    if aspsp == Aspsp.MEITAV:
        # meitav key_id
        key_id = "SN=394E517E00D3645F04A08F1609C13FC2F1244CF9,CA=CN=Test-OpenBankingIL%20Seal%20CA,OU=GCIO-eGOV-OBCA,2.5.4.97=NTRIL-50010037,O=Government%20Of%20Israel,C=IL"
    elif aspsp == Aspsp.ONE_ZERO:
        key_id = "SN=394E517E00D3645F04A08F1609C13FC2F1244CF9,CA=CN=Test-OpenBankingIL Seal CA,OU=GCIO-eGOV-OBCA,2.5.4.97=NTRIL-50010037,O=Government Of Israel,C=IL"
    else:
        # original key_id all
        key_id = "SN=394E517E00D3645F04A08F1609C13FC2F1244CF9,CA=CN=Test-OpenBankingIL Seal CA, OU=GCIO-eGOV-OBCA, 2.5.4.97=NTRIL-50010037, O=Government Of Israel, C=IL"

    # Algorithm
    algorithm = "rsa-sha256"

    # Encoded Key ID
    if aspsp == Aspsp.MEITAV or aspsp == Aspsp.ONE_ZERO:
        encoded_key_id = key_id
    else:
        encoded_key_id = urllib.parse.quote(key_id, safe='')

    # Digest

    """
    The "Digest" Header contains a Hash of the
    message body, if the message does not contain a body, the "Digest" header must contain the
    hash of an empty bytelist
    """
    digest_header = build_digest(body)

    # Headers for Signature
    headers_for_signature = "x-request-id digest consent-id psu-ip-address"

    if extra_headers and "psu_id_type" in extra_headers:
        headers_for_signature += " psu-id-type"

    if extra_headers and "psu_ip" in extra_headers:
        headers_for_signature += " psu-ip-address"

    # Headers for Signature values
    header_map = {
        "x-request-id": x_request_id,
        "digest": digest_header,
    }

    # if extra_headers and "psu_id" in extra_headers:
    #     header_map["psu-id"] = extra_headers["psu_id"]
    #
    # if extra_headers and "tpp-redirect-uri" in extra_headers:
    #     header_map["tpp-redirect-uri"] = extra_headers["tpp-redirect-uri"]

    if extra_headers:
        if "consent_id" in extra_headers:
            header_map["consent-id"] = extra_headers["consent_id"]

        if "psu_ip" in extra_headers:
            header_map["psu-ip-address"] = extra_headers["psu_ip"]

        if "psu_id_type" in extra_headers:
            header_map["psu-id-type"] = extra_headers["psu_id_type"]

    # if extra_headers and "access_token" in extra_headers:
    #     header_map["authorization"] = f"Bearer {extra_headers['access_token']}"

    # Build Signing String
    signing_string = '\n'.join(f"{h}: {header_map[h]}" for h in headers_for_signature.split())

    # qseal
    path_to_private_key_qseal_pem = config.SHAVVE_QSEAL_KEY_PATH
    private_key_qseal_password = config.SHAVVE_QSEAL_KEY_PW
    private_key = load_private_key(path_to_private_key_qseal_pem, private_key_qseal_password)

    # Sign the string
    signature = private_key.sign(
        signing_string.encode('utf-8'),
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    signature_base64 = base64.b64encode(signature).decode('utf-8')

    signature_header = (
        f'keyId="{encoded_key_id}",algorithm="{algorithm}",headers="{headers_for_signature}",signature="{signature_base64}"'
    )

    qseal_cert_b64_path = config.SHAVVE_QSEAL_CERT_PEM_PATH

    with open(qseal_cert_b64_path, 'r', encoding='utf-8') as f:
        qseal_cert_b64 = f.read()

    qseal_cert_b64 = re.sub(r'-----BEGIN CERTIFICATE-----|-----END CERTIFICATE-----', '', qseal_cert_b64)
    qseal_cert_b64 = re.sub(r'\s+', '', qseal_cert_b64).strip()

    # aspsp_config = get_aspsp_config(aspsp)  # Example for Discount, adjust as needed

    headers = {
        'X-Request-ID': x_request_id,
        # 'Date': date,
        # 'PSU-IP-Port': '443',
        'Digest': digest_header,
        'Signature': signature_header,
        'TPP-Signature-Certificate': qseal_cert_b64,
        'Content-Type': extra_headers.get('contentType', 'application/json')
    }

    # # Conditionally add optional headers
    # if extra_headers.get('psu_id'):
    #     headers['PSU-ID'] = extra_headers['psu_id']
    #
    if extra_headers.get('psu_id_type'):
        headers['PSU-ID-Type'] = extra_headers['psu_id_type']

    if extra_headers.get('psu_ip'):
        headers['PSU-IP-Address'] = extra_headers['psu_ip']
    #
    # if extra_headers.get('redirect_uri'):
    #     headers['TPP-Redirect-URI'] = extra_headers['redirect_uri']
    #
    # if extra_headers.get('notify_uri'):
    #     headers['TPP-Notification-URI'] = extra_headers['notify_uri']
    #
    if extra_headers.get('access_token'):
        headers['Authorization'] = f"Bearer {extra_headers['access_token']}"
    #
    if extra_headers.get('consent_id'):
        headers['Consent-ID'] = extra_headers['consent_id']

    return headers, x_request_id


@dataclass
class AspspConfig:
    ca_file_path: str
    psu_id_type: Optional[str]


def get_aspsp_registry() -> dict[str, AspspConfig]:
    return {
        Aspsp.DISCOUNT: AspspConfig(
            ca_file_path=config.DISCOUNT_CA_CERT_PATH,
            psu_id_type=None,
        ),
        Aspsp.LEUMI: AspspConfig(
            ca_file_path=config.LEUMI_CA_CERT_PATH,
            psu_id_type=None,
        ),
        Aspsp.MIZRAHI: AspspConfig(
            ca_file_path=config.MIZRAHI_CA_CERT_PATH,
            psu_id_type=None,
        ),
        Aspsp.POALIM: AspspConfig(
            ca_file_path=config.POALIM_CA_CERT_PATH,
            psu_id_type=None,
        ),
        Aspsp.PEPPER: AspspConfig(
            ca_file_path=config.PEPPER_CA_CERT_PATH,
            psu_id_type=None,
        ),
        Aspsp.CAL: AspspConfig(
            ca_file_path=config.CAL_CA_CERT_PATH,
            psu_id_type=None,
        ),
        Aspsp.YAHAV: AspspConfig(
            ca_file_path=config.YAHAV_CA_CERT_PATH,
            psu_id_type=None,
        ),
        Aspsp.MEITAV: AspspConfig(
            ca_file_path=config.MEITAV_CA_CERT_PATH,
            psu_id_type=None,
        ),
        Aspsp.MASSAD: AspspConfig(
            ca_file_path=config.FIBI_CA_CERT_PATH,
            psu_id_type='MASSAD',
        ),
        Aspsp.FIBI_OTZAR: AspspConfig(
            ca_file_path=config.FIBI_CA_CERT_PATH,
            psu_id_type='FIBI-OTZAR',
        ),
        Aspsp.FIBI_UBANK: AspspConfig(
            ca_file_path=config.FIBI_CA_CERT_PATH,
            psu_id_type='FIBI-UBANK',
        ),
        Aspsp.FIBI_BNL: AspspConfig(
            ca_file_path=config.FIBI_CA_CERT_PATH,
            psu_id_type='FIBI-BNL',
        ),
        Aspsp.FIBI_PAGI: AspspConfig(
            ca_file_path=config.FIBI_CA_CERT_PATH,
            psu_id_type='FIBI-PAGI',
        ),

    }


def get_aspsp_config(aspsp: Aspsp) -> AspspConfig:
    registry = get_aspsp_registry()
    if aspsp not in registry:
        raise ValueError(f"Unsupported ASPSP: {aspsp}")
    return registry[aspsp]
