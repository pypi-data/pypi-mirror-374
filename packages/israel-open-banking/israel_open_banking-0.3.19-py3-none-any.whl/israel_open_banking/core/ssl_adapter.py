import json
import shlex
import ssl

import requests
from requests.adapters import HTTPAdapter
from urllib3 import PoolManager


class SSLAdapter(HTTPAdapter):
    def __init__(self, certfile, keyfile, key_password, ca_cert, verify=True):
        self.certfile = certfile
        self.keyfile = keyfile
        self.key_password = key_password
        self.ca_cert = ca_cert
        self.verify = verify
        super().__init__()

    def init_poolmanager(self, *args, **kwargs):
        # Build an SSLContext first …
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

        # Client authentication (mTLS)
        ctx.load_cert_chain(
            certfile=self.certfile,
            keyfile=self.keyfile,
            password=self.key_password,
        )

        # Server-certificate policy
        if self.verify:
            # trust system CAs + optional extra bundle
            if self.ca_cert:
                ctx.load_verify_locations(cafile=self.ca_cert)
            ctx.verify_mode = ssl.CERT_REQUIRED
            ctx.check_hostname = True
        else:
            # **Insecure**: accept any cert
            ctx.check_hostname = False  # MUST be False first
            ctx.verify_mode = ssl.CERT_NONE

        # Hand the ready context to urllib3
        kwargs["ssl_context"] = ctx
        self.poolmanager = PoolManager(*args, **kwargs)


def send_get_request(
    url: str, headers: dict, qwac_cert: str, qwac_key: str, qwac_pw: str, ca_cert: str
) -> requests.Response:
    print_curl_command(url, headers, None, qwac_cert, qwac_key)

    session = requests.Session()
    session.mount(
        url.split("/")[0] + "//" + url.split("/")[2],
        SSLAdapter(
            certfile=qwac_cert, keyfile=qwac_key, key_password=qwac_pw, ca_cert=ca_cert, verify=False
        ),
    )

    response = session.get(url, headers=headers, timeout=30)
    print_response(response)
    return response



def send_post_request(
    url: str,
    headers: dict,
    data: any,
    qwac_cert: str,
    qwac_key: str,
    qwac_pw: str,
    ca_cert: str,
) -> requests.Response:
    print_curl_command(url, headers, data, qwac_cert, qwac_key)

    session = requests.Session()
    session.mount(
        url.split("/")[0] + "//" + url.split("/")[2],
        SSLAdapter(
            certfile=qwac_cert, keyfile=qwac_key, key_password=qwac_pw, ca_cert=ca_cert
        ),
    )

    response = session.post(url, headers=headers, data=data, timeout=30)
    return response

def print_curl_command(url, headers, data, cert_path=None, key_path=None):
    curl_parts = ["curl", "-X", "POST"]

    for key, value in headers.items():
        curl_parts += ["-H", f"{key}: {value}"]

    if data is not None:
        body = json.dumps(data)
        curl_parts += ["--data", shlex.quote(body)]

    if cert_path and key_path:
        curl_parts += ["--cert", cert_path, "--key", key_path]

    curl_parts.append(shlex.quote(url))

    print(" ".join(curl_parts))

def print_response(response: requests.Response):
    print(f"🔍 Response Status Code: {response.status_code}")
    print(f"📜 Response Headers: {response.headers}")
    if response.content:
        try:
            content = response.json()
        except json.JSONDecodeError:
            content = response.content
        print(f"📄 Response Content: {content}")
    else:
        print("📄 Response Content: No content")

