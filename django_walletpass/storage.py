from django.utils.module_loading import import_string
from django_walletpass.settings import dwpconfig as WALLETPASS_CONF

STORAGE_CLASS = import_string(WALLETPASS_CONF['STORAGE_CLASS'])


class WalletPassStorage(STORAGE_CLASS):
    pass
