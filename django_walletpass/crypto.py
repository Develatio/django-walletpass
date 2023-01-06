# pylint: disable=protected-access, invalid-name, too-many-locals
import base64
import secrets

from cryptography import x509
from cryptography.hazmat.bindings.openssl.binding import Binding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import pkcs7
from django.utils.crypto import salted_hmac

copenssl = Binding.lib
cffi = Binding.ffi


# SMIME isn't supported by pyca/cryptography:
# https://github.com/pyca/cryptography/issues/1621
def pkcs7_sign(
    certcontent,
    keycontent,
    wwdr_certificate,
    data,
    key_password=None,
    flag=copenssl.PKCS7_BINARY | copenssl.PKCS7_DETACHED,
):
    """Sign data with PKCS#7.

    Args:
        keycontent (bytes): Content of pem file certificate
        keycontent (bytes): Content of key file
        wwdr_certificate (bytes): Content of Intermediate cert file
        data (bytes): Data to be signed
        key_password (bytes, optional): key file passwd. Defaults to None.
        flag (int, optional): Flags to be passed to PKCS7_sign C lib.
            Defaults to copenssl.PKCS7_BINARY|copenssl.PKCS7_DETACHED.
    """

    cert = x509.load_pem_x509_certificate(certcontent)
    key = serialization.load_pem_private_key(keycontent, key_password)
    options = [
        pkcs7.PKCS7Options.Binary,
        pkcs7.PKCS7Options.DetachedSignature,
    ]
    return (
        pkcs7.PKCS7SignatureBuilder()
        .set_data(data)
        .add_signer(cert, key, hashes.SHA256())
        .sign(serialization.Encoding.SMIME, options)
    )


def gen_random_token():
    rand1 = secrets.token_bytes(16)
    rand2 = secrets.token_bytes(7)
    rand2 = salted_hmac(rand1, rand2).digest()
    part_a = base64.urlsafe_b64encode(rand2).rstrip(b"=").decode("ascii")
    part_b = secrets.token_urlsafe(20)
    return part_b + part_a
