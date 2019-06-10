import os
from django.conf import settings as django_settings

FULL_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WALLETPASS_CONF = {
    'CERT_PATH': None,
    'KEY_PATH': None,
    'KEY_PASSWORD': None,
    'APPLE_WWDRCA_CERT_PATH': os.path.join(FULL_BASE_DIR, 'certs', 'AppleWWDRCA.cer'),
    'APPLE_WWDRCA_PEM_PATH': os.path.join(FULL_BASE_DIR, 'certs', 'AppleWWDRCA.pem'),
    'PASS_TYPE_ID': None,
    'TEAM_ID': None,
    'SERVICE_URL': None,
    'WALLETPASS_PUSH_CLASS': 'django_walletpass.services.PushBackend',
    'PUSH_SANDBOX': False,
    'STORAGE_CLASS': django_settings.DEFAULT_FILE_STORAGE,
    'UPLOAD_TO': 'passes'
}

if getattr(django_settings, 'WALLETPASS', None):
    WALLETPASS_CONF.update(django_settings.WALLETPASS)

CERT_CONTENT = open(WALLETPASS_CONF['CERT_PATH'], 'rb').read()
KEY_CONTENT = open(WALLETPASS_CONF['KEY_PATH'], 'rb').read()
WWDRCA_CONTENT = open(WALLETPASS_CONF['APPLE_WWDRCA_CERT_PATH'], 'rb').read()
