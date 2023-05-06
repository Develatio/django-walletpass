from django.apps import AppConfig


class DjangoWalletpassConfig(AppConfig):
    name = "django_walletpass"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from django_walletpass import (
            signals as _signals,
        )  # pylint: disable=import-outside-toplevel
