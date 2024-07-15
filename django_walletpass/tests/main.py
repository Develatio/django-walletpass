import datetime
import json
from unittest import mock

from dateutil.parser import parse
from django.contrib import admin
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory

from django_walletpass import crypto
from django_walletpass.admin import PassAdmin
from django_walletpass.classviews import FORMAT, RegisterPassViewSet, LogViewSet
from django_walletpass.models import Pass, PassBuilder, Registration, Log

from django_walletpass.settings import dwpconfig as WALLETPASS_CONF


class AdminTestCase(TestCase):
    def test_wallet_pass(self):
        admin_view = PassAdmin(Pass, admin.site)
        builder = PassBuilder()
        builder.pass_data = {
            "formatVersion": 1,
            "barcode": {
                "message": "123456789",
                "format": "PKBarcodeFormatPDF417",
                "messageEncoding": "iso-8859-1",
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

        self.assertTrue(
            "<img src='/static/admin/passbook_icon.svg'/>" in
            admin_view.wallet_pass_(instance)
        )


class ClassViewsTestCase(TestCase):
    def test_format_parse(self):
        """ensure dateutil reads FORMAT properly"""
        now = timezone.now()
        now_string = now.strftime(FORMAT)
        self.assertEqual(
            parse(now_string), timezone.make_naive(now).replace(microsecond=0)
        )


class CryptoTestCase(TestCase):
    def test_smime_sign(self):
        crypto.pkcs7_sign(
            certcontent=WALLETPASS_CONF["CERT_CONTENT"],
            keycontent=WALLETPASS_CONF["KEY_CONTENT"],
            wwdr_certificate=WALLETPASS_CONF["WWDRCA_PEM_CONTENT"],
            data=b"data to be signed",
            key_password=WALLETPASS_CONF["KEY_PASSWORD"],
        )


class BuilderTestCase(TestCase):
    def test_build_pkpass(self):
        builder = PassBuilder()
        builder.pass_data = {
            "formatVersion": 1,
            "barcode": {
                "message": "123456789",
                "format": "PKBarcodeFormatPDF417",
                "messageEncoding": "iso-8859-1",
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

        builder2.pass_data.update({"organizationName": "test"})
        builder2.build()
        builder2.write_to_model(instance)
        instance.save()

        builder3 = instance.get_pass_builder()
        builder3.build()

        self.assertEqual(builder2.manifest_dict, builder3.manifest_dict)
        self.assertEqual(builder2.pass_data, builder3.pass_data)

        self.assertNotEqual(builder.manifest_dict, builder3.manifest_dict)
        self.assertNotEqual(builder.pass_data, builder3.pass_data)


class ModelTestCase(TestCase):
    @mock.patch("django_walletpass.models.Pass.get_registrations")
    @mock.patch("django_walletpass.services.APNs.send_notification")
    def test_push_notification(self, send_notification_mock, get_registrations_mock):
        get_registrations_mock.return_value = [Registration()]
        pass_ = Pass(pk=1)
        with mock.patch("django_walletpass.services.APNs.__init__", return_value=None):
            pass_.push_notification()
            send_notification_mock.assert_called_with(mock.ANY)
            request = send_notification_mock.call_args_list[0][0][0]
            self.assertEqual(request.message, {"aps": {}})


class RegisterPassViewSetTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        builder = PassBuilder()
        builder.pass_data = {
            "formatVersion": 1,
            "barcode": {
                "message": "123456789",
                "format": "PKBarcodeFormatPDF417",
                "messageEncoding": "iso-8859-1",
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
        self.pass_instance = instance
        self.pass_type_id = instance.pass_type_identifier
        self.device_library_id = 'ebc6fdbd52ffd906fc294aba259f239c'
        self.registration = Registration.objects.create(
            device_library_identifier=self.device_library_id,
            pazz=self.pass_instance
        )
        self.view = RegisterPassViewSet.as_view({'delete': 'destroy'})

    def test_destroy_registration_exists(self):
        existing_url = reverse(
            'walletpass_register_pass',
            args=[
                self.device_library_id,
                self.pass_type_id,
                self.pass_instance.serial_number
            ],
            urlconf='django_walletpass.urls')

        self.assertEqual(Registration.objects.count(), 1)
        request = self.factory.delete(existing_url,
                                      HTTP_AUTHORIZATION=f'ApplePass {self.pass_instance.authentication_token}')
        response = self.view(request,
                             device_library_id=self.device_library_id,
                             pass_type_id=self.pass_instance.pass_type_identifier,
                             serial_number=self.pass_instance.serial_number)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Registration.objects.filter(device_library_identifier=self.device_library_id,
                                                     pazz=self.pass_instance).exists())
        self.assertEqual(Registration.objects.count(), 0)

    def test_destroy_registration_not_exists(self):
        non_existing_device_library_id = 'd4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9'
        non_existing_url = reverse(
            'walletpass_register_pass',
            args=[
                non_existing_device_library_id,
                self.pass_type_id,
                self.pass_instance.serial_number
            ],
            urlconf='django_walletpass.urls'
        )
        self.assertEqual(Registration.objects.count(), 1)

        request = self.factory.delete(non_existing_url,
                                      HTTP_AUTHORIZATION=f'ApplePass {self.pass_instance.authentication_token}')
        response = self.view(request,
                             device_library_id=non_existing_device_library_id,
                             pass_type_id=self.pass_type_id,
                             serial_number=self.pass_instance.serial_number)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Registration.objects.count(), 1)
        self.assertTrue(Registration.objects.filter(device_library_identifier=self.device_library_id,
                                                    pazz=self.pass_instance).exists())


class LogViewSetTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_create_log(self):
        url = reverse('walletpass_log', urlconf='django_walletpass.urls')
        expected_timestamp_str = "2024-07-08 10:22:35 AM +0200"
        data = {
            'logs': [f"[{expected_timestamp_str}] Web service error for pass.com.develatio.devpubs.example ("
                     "https://example.com/passes/): Response to 'What changed?' "
                     "request included 1 serial numbers but the lastUpdated tag (2024-07-08T08:03:13.588412+00:00) "
                     "remained the same."]
        }
        request = self.factory.post(url, data=json.dumps(data), content_type='application/json')
        view = LogViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        created_log = Log.objects.first()
        self.assertIsNotNone(created_log)
        expected_timestamp = datetime.datetime.strptime(expected_timestamp_str, "%Y-%m-%d %I:%M:%S %p %z")
        expected_utc_timestamp = expected_timestamp.astimezone(timezone.utc)

        self.assertEqual(created_log.created_at, expected_utc_timestamp)
