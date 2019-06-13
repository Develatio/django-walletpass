from django.db.models.signals import post_save
from django.utils.module_loading import import_string
from django.dispatch import receiver
from django_walletpass.models import Pass
from django_walletpass.settings import dwpconfig as WALLETPASS_CONF


@receiver(post_save, sender=Pass)
def fill_total(instance=None, **_kwargs):
    klass = import_string(WALLETPASS_CONF['WALLETPASS_PUSH_CLASS'])
    push_module = klass()
    for registration in instance.registrations.all():
        push_module.push_notification_from_instance(registration)
