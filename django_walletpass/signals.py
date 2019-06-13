from django.db.models.signals import post_save
from django.dispatch import receiver
from django_walletpass.models import Pass


@receiver(post_save, sender=Pass)
def send_push_notification(instance=None, **_kwargs):
    instance.push_notification()
