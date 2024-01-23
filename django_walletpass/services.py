import asyncio
import logging
from ssl import SSLError

from aioapns import APNs, NotificationRequest
from aioapns.exceptions import ConnectionClosed
from django_walletpass.models import Registration
from django_walletpass.settings import dwpconfig as WALLETPASS_CONF

logger = logging.getLogger('walletpass.services')


class PushBackend:
    def __init__(self):
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

    async def push_notification(self, client, token):

        try:
            request = NotificationRequest(device_token=token, message={"aps": {}},)
            response = await client.send_notification(request)
            return response

        except SSLError as e:
            logger.error("django_walletpass SSLError: %s", e)
        except (ConnectionError, ConnectionClosed) as e:
            logger.error("django_walletpass StreamResetError. Bad cert or token? %s", e)
        # Errors should never pass silently.
        except Exception as e:  # pylint: disable=broad-except
            # Unless explicitly silenced.
            logger.error("django_walletpass uncaught error %s", e)

    def push_notification_with_token(self, token):
        client = APNs(
            key=WALLETPASS_CONF["TOKEN_AUTH_KEY_PATH"],
            key_id=WALLETPASS_CONF["TOKEN_AUTH_KEY_ID"],
            team_id=WALLETPASS_CONF["TEAM_ID"],
            topic=WALLETPASS_CONF["PASS_TYPE_ID"],
            use_sandbox=WALLETPASS_CONF["PUSH_SANDBOX"],
        )
        return self.loop.run_until_complete(self.push_notification(client, token))

    def push_notification_from_instance(self, registration_instance):
        return self.push_notification_with_token(registration_instance.push_token)

    def push_notification_from_pk(self, registration_pk):
        registration = Registration.objects.get(pk=registration_pk)
        return self.push_notification_from_instance(registration)
