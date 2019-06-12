from django.test import TestCase
from django_walletpass import crypto
from django_walletpass.models import PassBuilder
from django_walletpass.settings import dwpconfig as WALLETPASS_CONF


class CryptoTestCase(TestCase):
    def test_smime_sign(self):
        crypto.pkcs7_sign(
            certcontent=WALLETPASS_CONF['CERT_CONTENT'],
            keycontent=WALLETPASS_CONF['KEY_CONTENT'],
            wwdr_certificate=WALLETPASS_CONF['WWDRCA_CONTENT'],
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

        instance = builder.write_to_model()
        instance.save()
        self.assertIsNotNone(instance.pk)

        builder2 = instance.get_pass_builder()
        builder2.build()
        self.assertEqual(builder.manifest_dict, builder2.manifest_dict)
        self.assertEqual(builder.pass_data, builder2.pass_data)

        builder2.pass_data.update({"organizationName": 'test'})
        builder2.build()
        builder2.write_to_model(instance)
        instance.save()

        builder3 = instance.get_pass_builder()
        builder3.build()

        self.assertEqual(builder2.manifest_dict, builder3.manifest_dict)
        self.assertEqual(builder2.pass_data, builder3.pass_data)

        self.assertNotEqual(builder.manifest_dict, builder3.manifest_dict)
        self.assertNotEqual(builder.pass_data, builder3.pass_data)
