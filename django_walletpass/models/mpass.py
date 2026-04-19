from django.db import models
from django.utils.module_loading import import_string

from django_walletpass.settings import dwpconfig as WALLETPASS_CONF
from django_walletpass.storage import WalletPassStorage


class Pass(models.Model):
    """
    Pass instance
    """
    pass_type_identifier = models.CharField(max_length=150)
    serial_number = models.CharField(max_length=150)
    authentication_token = models.CharField(max_length=150)
    data = models.FileField(
        upload_to=WALLETPASS_CONF['UPLOAD_TO'],
        storage=WalletPassStorage(),
    )
    updated_at = models.DateTimeField(auto_now=True)

    def get_registrations(self):
        return self.registrations.all()

    def push_notification(self):
        klass = import_string(WALLETPASS_CONF['WALLETPASS_PUSH_CLASS'])
        push_module = klass()
        for registration in self.get_registrations():
            response = push_module.push_notification_from_instance(registration)
            # delete invalid registration
            if response.status == '410':
                registration.delete()

    def __unicode__(self):
        return self.serial_number

    def __str__(self):
        return str(self.serial_number)

    class Meta:
        verbose_name_plural = "passes"
        unique_together = (
            'pass_type_identifier',
            'serial_number',
        )
