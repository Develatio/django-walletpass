import os
from collections import UserDict
from django.conf import settings as django_settings
from django.test.signals import setting_changed

FULL_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULTS = {
    'CERT_PATH': None,
    'CERT_CONTENT': None,
    'KEY_CONTENT': None,
    'WWDRCA_CONTENT': None,
    'KEY_PATH': None,
    'KEY_PASSWORD': None,
    'APPLE_WWDRCA_CERT_PATH': os.path.join(FULL_BASE_DIR, 'certs', 'AppleWWDRCA.cer'),
    'WWDRCA_CONTENT': open(os.path.join(FULL_BASE_DIR, 'certs', 'AppleWWDRCA.cer'), 'rb').read(),
    'APPLE_WWDRCA_PEM_PATH': os.path.join(FULL_BASE_DIR, 'certs', 'AppleWWDRCA.pem'),
    'PASS_TYPE_ID': None,
    'TEAM_ID': None,
    'SERVICE_URL': None,
    'WALLETPASS_PUSH_CLASS': 'django_walletpass.services.PushBackend',
    'PUSH_SANDBOX': False,
    'STORAGE_CLASS': django_settings.DEFAULT_FILE_STORAGE,
    'STORAGE_HTTP_REDIRECT': False,
    'UPLOAD_TO': 'passes',
}


class ConfigManager(UserDict):
    def update_conf(self):
        self.data = DEFAULTS
        new = django_settings.WALLETPASS
        if 'CERT_PATH' in new:
            new['CERT_CONTENT'] = open(new['CERT_PATH'], 'rb').read()
        if 'KEY_PATH' in new:
            new['KEY_CONTENT'] = open(new['KEY_PATH'], 'rb').read()
        if 'APPLE_WWDRCA_CERT_PATH' in new:
            new['WWDRCA_CONTENT'] = open(new['APPLE_WWDRCA_CERT_PATH'], 'rb').read()
        self.data.update(new)


dwpconfig = ConfigManager(DEFAULTS)
dwpconfig.update_conf()


def update_conf(*args, **kwargs):
    if kwargs['setting'] == 'WALLETPASS':
        dwpconfig.update_conf()


setting_changed.connect(update_conf)
