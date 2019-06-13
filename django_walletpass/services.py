import logging
from ssl import SSLError
from hyper.tls import init_context
from hyper.http20.exceptions import StreamResetError
from apns2.client import APNsClient
from apns2.credentials import Credentials
from apns2.payload import Payload
from django_walletpass.models import Registration
from django_walletpass.settings import dwpconfig as WALLETPASS_CONF

logger = logging.getLogger('django.contrib.gis')


class PushBackend:
    def push_notification(self, credentials, push_sandbox, pass_type_id, push_token):
        payload = Payload()
        try:
            client = APNsClient(
                credentials,
                use_sandbox=push_sandbox,
                use_alternative_port=False,
            )
            client.send_notification(
                push_token,
                payload,
                pass_type_id,
            )
        except SSLError as e:
            logger.error("django_walletpass SSLError: %s", e)
        except StreamResetError as e:
            logger.error("django_walletpass StreamResetError. Bad cert or token? %s", e)
        # Errors should never pass silently.
        except Exception as e:
            # Unless explicitly silenced.
            logger.error("django_walletpass uncaught error %s", e)

    def get_credentials(self):
        context = init_context(
            cert=(
                WALLETPASS_CONF['CERT_PATH'],
                WALLETPASS_CONF['KEY_PATH'],
            ),
            # cert_path=WALLETPASS_CONF['APPLE_WWDRCA_PEM_PATH'],
            cert_password=WALLETPASS_CONF['KEY_PASSWORD'],
        )

        return Credentials(context)

    def push_notification_with_token(self, token):
        self.push_notification(
            self.get_credentials(),
            push_sandbox=WALLETPASS_CONF['PUSH_SANDBOX'],
            pass_type_id=WALLETPASS_CONF['PASS_TYPE_ID'],
            push_token=token,
        )

    def push_notification_from_instance(self, registration_instance):
        self.push_notification_with_token(registration_instance.push_token)

    def push_notification_from_pk(self, registration_pk):
        registration = Registration.objects.get(pk=registration_pk)
        return self.push_notification_from_instance(registration)
