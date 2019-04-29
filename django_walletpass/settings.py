from django.conf import settings

WALLETPASS_CERT = getattr(settings, 'WALLETPASS_CERT', '')
WALLETPASS_CERT_KEY = getattr(settings, 'WALLETPASS_CERT_KEY', '')
