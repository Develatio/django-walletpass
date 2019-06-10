# pylint: disable=protected-access, invalid-name, too-many-locals
import secrets
import base64
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.bindings.openssl.binding import Binding
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from django.utils.crypto import salted_hmac

copenssl = Binding.lib
cffi = Binding.ffi


# SMIME isn't supported by pyca/cryptography:
# https://github.com/pyca/cryptography/issues/1621
def pkcs7_sign(certcontent,
               keycontent,
               wwdr_certificate,
               data,
               key_password=None,
               flag=copenssl.PKCS7_BINARY | copenssl.PKCS7_DETACHED):
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

    backend = default_backend()

    # Load cert and key
    pkey = load_pem_private_key(keycontent, key_password, backend=backend)
    cert = x509.load_pem_x509_certificate(certcontent, backend=backend)

    # Load intermediate cert and push it into < Cryptography_STACK_OF_X509 * >
    intermediate_cert = x509.load_der_x509_certificate(
        wwdr_certificate,
        backend,
    )
    certs_stack = copenssl.sk_X509_new_null()
    # https://www.openssl.org/docs/man1.1.1/man3/sk_TYPE_push.html
    # int sk_TYPE_push(STACK_OF(TYPE) *sk, const TYPE *ptr);
    # return amount of certs into certs_stack, -1 on error
    # TODO: raise on count < 1
    _count = copenssl.sk_X509_push(certs_stack, intermediate_cert._x509)

    bio = backend._bytes_to_bio(data)
    # From
    # pyca/cryptography/src/_cffi_src/openssl/pkcs7.py
    # PKCS7 *PKCS7_sign(X509 *, EVP_PKEY *,
    #                   Cryptography_STACK_OF_X509 *, BIO *, int);
    # signing-time attr is automatically added:
    # https://www.openssl.org/docs/man1.1.1/man3/PKCS7_sign.html
    pkcs7 = copenssl.PKCS7_sign(
        cert._x509,
        pkey._evp_pkey,
        certs_stack,
        bio.bio,
        flag,
    )

    bio_out = backend._create_mem_bio_gc()
    copenssl.i2d_PKCS7_bio(bio_out, pkcs7)

    signed_pkcs7 = backend._read_mem_bio(bio_out)
    return signed_pkcs7


def gen_random_token():
    rand1 = secrets.token_bytes(16)
    rand2 = secrets.token_bytes(7)
    rand2 = salted_hmac(rand1, rand2).digest()
    part_a = base64.urlsafe_b64encode(rand2).rstrip(b'=').decode('ascii')
    part_b = secrets.token_urlsafe(20)
    return part_b + part_a
