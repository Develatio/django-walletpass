from django.test import TestCase
from django_walletpass import crypto
from django_walletpass.models import PassBuilder
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


class BuilderTestCase(TestCase):
    def test_build_pkpass(self):
        builder = PassBuilder()
        builder.pass_data = {
            "formatVersion": 1,
            "barcode": {
                "message": "123456789",
                "format": "PKBarcodeFormatPDF417",
                "messageEncoding": "iso-8859-1"
            },
            "organizationName": "Organic Produce",
            "description": "Organic Produce Loyalty Card",
            "logoText": "Organic Produce",
            "foregroundColor": "rgb(255, 255, 255)",
            "backgroundColor": "rgb(55, 117, 50)",
        }

        builder.build()

        instance = builder.save_to_db()
        self.assertIsNotNone(instance.pk)

        builder2 = instance.get_pass_builder()
        self.assertEqual(builder.manifest_dict, builder2.manifest_dict)
