django-walletpass
===============

This application implements the creation of **signed .pkpass** files and
**API endpoints** for pass registration, updates and logging.

Requirements
============

- Django 2.*
- openssl (for .pkpass sign with pyca/cryptography C bindings)

Getting Started
===============

```
$ pip install django-walletpass
```

Add 'django_walletpass' to you installed apps in the settings.py file.

Load the content of your certificates in your settings.py file. This is a good
place to use your secrets strategy, just remember that the content of
`WALLETPASS_CERTIFICATES_P12` and `WALLETPASS_CERTIFICATES_P12_PASSWORD` should
be in `bytes` format.

```
# Your Certificates.p12 content in bytes format
WALLETPASS_CERTIFICATES_P12 = open('path/to/your/Certificates.p12', 'rb').read()

# The password for Certificates.p12 (None if isn't protected)
WALLETPASS_CERTIFICATES_P12_PASSWORD = "mypassword"
```


You should also import the urls in your site urls.
```
urlpatterns = [
    url(r'^api/', include('django_walletpass.urls')),
```

django-walletpass signals certain events that might come handy in your
application.

```
from django_walletpass.views import pass_registered, pass_unregistered
@receiver(pass_registered)
def pass_registered(sender, **kwargs):
    pass

@receiver(pass_unregistered)
def pass_unregistered(sender, **kwargs):
    pass
```

Specification
=============

The complete specification can be found in the [Passbook Web Service Reference](https://developer.apple.com/library/prerelease/ios/#documentation/PassKit/Reference/PassKit_WebService/WebService.html).
