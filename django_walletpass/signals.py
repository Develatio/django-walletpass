from django.db.models.signals import post_save
from django.dispatch import receiver
from django_walletpass.models import Pass


@receiver(post_save, sender=Pass)
async def send_push_notification(instance=None, **_kwargs):
    await instance.push_notification()
