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
# adjusted with latest cryptography code from https://github.com/devartis/passbook/pull/60/files
def pkcs7_sign(
    certcontent, keycontent, wwdr_certificate, data, key_password=None,
):
    """Sign data with PKCS#7.

    Args:
        keycontent (bytes): Content of pem file certificate
        keycontent (bytes): Content of key file
        wwdr_certificate (bytes): Content of Intermediate cert file
        data (bytes): Data to be signed
        key_password (bytes, optional): key file passwd. Defaults to None.
    """

    cert = x509.load_pem_x509_certificate(certcontent)
    priv_key = serialization.load_pem_private_key(keycontent, password=key_password)
    wwdr_cert = x509.load_pem_x509_certificate(wwdr_certificate)

    options = [pkcs7.PKCS7Options.DetachedSignature]
    return (
        pkcs7.PKCS7SignatureBuilder()
        .set_data(data)
        .add_signer(cert, priv_key, hashes.SHA256())
        .add_certificate(wwdr_cert)
        .sign(serialization.Encoding.DER, options)
    )


def gen_random_token():
    rand1 = secrets.token_bytes(16)
    rand2 = secrets.token_bytes(7)
    rand2 = salted_hmac(rand1, rand2).digest()
    part_a = base64.urlsafe_b64encode(rand2).rstrip(b'=').decode('ascii')
    part_b = secrets.token_urlsafe(20)
    return part_b + part_a
