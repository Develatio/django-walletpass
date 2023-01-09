import os
from collections import UserDict
from django.conf import settings as django_settings
from django.test.signals import setting_changed

FULL_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(FULL_BASE_DIR, 'certs', 'AppleWWDRCA.pem'), 'rb') as _ffile:
    wwdrca_pem_content = _ffile.read()

with open(os.path.join(FULL_BASE_DIR, 'certs', 'AppleWWDRCA.cer'), 'rb') as _ffile:
    wwdrca_content = _ffile.read()

DEFAULTS = {
    'PUSH_AUTH_STRATEGY': 'legacy',  # legacy or token
    'TOKEN_AUTH_KEY_PATH': None,
    'TOKEN_AUTH_KEY_ID': None,
    'CERT_PATH': None,
    'CERT_CONTENT': None,
    'KEY_CONTENT': None,
    'KEY_PATH': None,
    'KEY_PASSWORD': None,
    'APPLE_WWDRCA_CERT_PATH': os.path.join(FULL_BASE_DIR, 'certs', 'AppleWWDRCA.cer'),
    'WWDRCA_CONTENT': wwdrca_content,
    'APPLE_WWDRCA_PEM_PATH': os.path.join(FULL_BASE_DIR, 'certs', 'AppleWWDRCA.pem'),
    'WWDRCA_PEM_CONTENT': wwdrca_pem_content,
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
            with open(new['CERT_PATH'], 'rb') as ffile:
                new['CERT_CONTENT'] = ffile.read()
        if 'KEY_PATH' in new:
            with open(new['KEY_PATH'], 'rb') as ffile:
                new['KEY_CONTENT'] = ffile.read()
        if 'APPLE_WWDRCA_PEM_PATH' in new:
            with open(new['APPLE_WWDRCA_PEM_PATH'], 'rb') as ffile:
                new['WWDRCA_PEM_CONTENT'] = ffile.read()

        self.data.update(new)


dwpconfig = ConfigManager(DEFAULTS)
dwpconfig.update_conf()


def update_conf(*args, **kwargs):  # pylint: disable=unused-argument
    if kwargs['setting'] == 'WALLETPASS':
        dwpconfig.update_conf()


setting_changed.connect(update_conf)
