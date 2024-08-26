from aioapns.common import APNS_RESPONSE_CODE
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

from django_walletpass.models import Pass, Registration

TOKEN_UNREGISTERED = Signal()
PASS_REGISTERED = Signal()
PASS_UNREGISTERED = Signal()


@receiver(post_save, sender=Pass)
def send_push_notification(instance=None, **_kwargs):
    instance.push_notification()


@receiver(TOKEN_UNREGISTERED)
def delete_registration(
    sender,  # pylint: disable=unused-argument
    notification_request=None,
    notification_result=None,
    **kwargs  # pylint: disable=unused-argument
):
    if notification_result.status == APNS_RESPONSE_CODE.GONE:
        registration = Registration.objects.get(
            push_token=notification_request.device_token
        )
        pass_ = registration.pazz
        registration.delete()
        PASS_UNREGISTERED.send(sender=pass_)
