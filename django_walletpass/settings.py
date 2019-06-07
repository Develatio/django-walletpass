import os
from django.conf import settings

FULL_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if getattr(settings, 'APPLE_WWDRCA_CERT', None):
    APPLE_WWDRCA_CERT = settings.APPLE_WWDRCA_CERT
else:
    APPLE_WWDRCA_CERT = open(os.path.join(FULL_BASE_DIR, 'certs', 'AppleWWDRCA.cer'), 'rb').read()
