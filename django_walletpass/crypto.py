# pylint: disable=protected-access, invalid-name, too-many-locals
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.bindings.openssl.binding import Binding
from cryptography.hazmat.primitives.serialization import pkcs12

copenssl = Binding.lib
cffi = Binding.ffi


# SMIME isn't supported by pyca/cryptography:
# https://github.com/pyca/cryptography/issues/1621
def pkcs7_sign(p12_certificate,
               wwdr_certificate,
               data,
               certificate_password=None,
               flag=copenssl.PKCS7_BINARY | copenssl.PKCS7_DETACHED):
    """Sign data with PKCS#7.

    Args:
        p12_certificate (bytes): Content of Certificates.p12
        wwdr_certificate (bytes): Content of Intermediate cert
        data (bytes): Data to be signed
        certificate_password (str, optional): .p12 cert pass. Defaults to None.
        flag (int, optional): Flags to be passed to PKCS7_sign C lib.
            Defaults to copenssl.PKCS7_BINARY|copenssl.PKCS7_DETACHED.
    """

    backend = default_backend()
    # Load Certificates.p12
    pkey, cert, _ = pkcs12.load_key_and_certificates(
        p12_certificate,
        bytes(certificate_password, 'utf8'),
        backend,
    )

    # Load intermediate cert and push it into Cryptography_STACK_OF_X509 *
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
    pkcs7 = copenssl.PKCS7_sign(
        cert._x509,
        pkey._evp_pkey,
        certs_stack,
        bio.bio,
        flag,
    )

    bio_out = backend._create_mem_bio_gc()
    copenssl.PEM_write_bio_PKCS7(bio_out, pkcs7)

    signed_pkcs7 = backend._read_mem_bio(bio_out)
    return signed_pkcs7
