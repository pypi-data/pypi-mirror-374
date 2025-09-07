from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
import base64


def load_private_key(path: str, password: str) -> rsa.RSAPrivateKey:
    with open(path, "rb") as fh:
        return serialization.load_pem_private_key(fh.read(), password=password.encode())


def load_cert_base64(path: str) -> str:
    with open(path) as fh:
        lines = fh.read().splitlines()
    return "".join([line for line in lines if "-----" not in line])


def sign_string(signing_string: str, private_key: rsa.RSAPrivateKey) -> str:
    signature = private_key.sign(
        signing_string.encode('utf-8'),
        padding.PKCS1v15(),            # Equivalent to Node's RSA_PKCS1_PADDING
        hashes.SHA256()                # Same as 'sha256'
    )
    return base64.b64encode(signature).decode('utf-8')