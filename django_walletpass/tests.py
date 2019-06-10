from django.test import TestCase
from django.conf import settings
from django_walletpass import crypto
from django_walletpass.settings import (
    WALLETPASS_CONF,
    CERT_CONTENT,
    KEY_CONTENT,
    WWDRCA_CONTENT,
)


class CryptoTestCase(TestCase):
    def test_smime_sign(self):
        res = crypto.pkcs7_sign(
            certcontent=CERT_CONTENT,
            keycontent=KEY_CONTENT,
            wwdr_certificate=WWDRCA_CONTENT,
            data=b'data to be signed',
            key_password=WALLETPASS_CONF['KEY_PASSWORD'],
        )
