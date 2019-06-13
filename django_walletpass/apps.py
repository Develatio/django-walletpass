from django.apps import AppConfig


class DjangoWalletpassConfig(AppConfig):
    name = 'django_walletpass'

    def ready(self):
        from django_walletpass import signals as _signals
