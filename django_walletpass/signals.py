from django.db.models.signals import post_save
from django.utils.module_loading import import_string
from django.dispatch import receiver
from django_walletpass.settings import dwpconfig as WALLETPASS_CONF
from django_walletpass.models import Pass


@receiver(post_save, sender=Pass)
def send_push_notification(instance=None, **_kwargs):
    instance.push_notification()
