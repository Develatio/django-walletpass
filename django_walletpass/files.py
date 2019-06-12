from django.core.files.base import ContentFile

class WalletpassContentFile(ContentFile):
    content_type = 'application/vnd.apple.pkpass'
