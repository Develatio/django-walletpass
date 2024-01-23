from django.apps import AppConfig


class DjangoWalletpassConfig(AppConfig):
    name = 'django_walletpass'
    verbose_name = 'Django walletpass'

    def ready(self):
        from django_walletpass import signals as _signals  # pylint: disable=import-outside-toplevel
