from django.test import TestCase
from django.conf import settings
from django_walletpass import crypto
import django_walletpass.settings as dwp_settings


class CryptoTestCase(TestCase):
    def test_smime_sign(self):
        res = crypto.pkcs7_sign(
            settings.WALLETPASS_CERTIFICATES_P12,
            dwp_settings.APPLE_WWDRCA_CERT,
            b'data to be signed',
            settings.WALLETPASS_CERTIFICATES_P12_PASSWORD,
        )
