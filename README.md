![PyPI](https://img.shields.io/pypi/v/django-walletpass.svg)
![t](https://img.shields.io/badge/status-beta-red.svg)


# django-walletpass


This application implements the creation of **signed .pkpass** files and
**API endpoints** for pass registration, updates and logging.

## Requirements

- Django 2.*
- python >= 3.5
- pyca/cryptography (for .pkpass sign with pyca/cryptography C bindings)

## Getting Started

### Install

```
$ pip install django-walletpass
```

### Configure

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

Add extra needed conf to your settings.py file.

```
WALLETPASS_PASS_TYPE_ID = ""
WALLETPASS_TEAM_ID = ""
WALLETPASS_SERVICE_URL = ""
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

## Build and sign passes

### Init builder object:

Init empty builder

```
from django_walletpass.models import  PassBuilder
builder = PassBuilder()
```

Init builder usign a directory as base

```
from django_walletpass.models import  PassBuilder
builder = PassBuilder(directory='/path/to/your.pass/')
```

If the base directory contains a `pass.json` it will be loaded, but remember
that required attributes of `pass.json` will be overwritten during build process
using this values:

```
{
    "passTypeIdentifier": settings.WALLETPASS_PASS_TYPE_ID,
    "serialNumber": secrets.token_urlsafe(20),
    "teamIdentifier": settings.WALLETPASS_TEAM_ID,
    "webServiceURL": settings.WALLETPASS_SERVICE_URL,
    "authenticationToken": crypto.gen_random_token(),
}
```

### Handle pass.json data

To handle `pass.json` data, there is a dict inside your builder instance, you
can manage it like a normal python dictionary.


Update some attrs:

```
builder.pass_data.update({
  "barcode": {
    "message": "123456789",
    "format": "PKBarcodeFormatPDF417",
    "messageEncoding": "iso-8859-1"
  },
  "organizationName": "Organic Produce",
  "description": "Organic Produce Loyalty Card",
})
```

Update one attr:

```
builder.pass_data['description'] = "Organic Produce Loyalty Card"
```

### Overwrite automatically generated required attribute values

```
builder.pass_data_required.update({
    "passTypeIdentifier": "customvalue",
    "serialNumber": "customvalue",
    "teamIdentifier": "customvalue",
    "webServiceURL": "customvalue",
    "authenticationToken": "customvalue",
})
```

you can overwrite individual attributes:


```
builder.pass_data_required.update({
    "serialNumber": "customvalue",
})
builder.pass_data_required['serialNumber] = 'cutomvalue'
```

### Add extra files

```
file_content = open('myfile', 'rb').read()
builder.add_file('image.png', file_content)
```

You can also add files to directories:

```
file_content = open('myfile', 'rb').read()
builder.add_file('en.lproj/pass.strings', file_content)
```


### Build .pkpass

Build the content of .pkpass

```
pkpass_content = builder.build()
```

Write to file:

```
pkpass_file = open('mypass.pkpass', 'rb')
pkpass_file.write(pkpass_content)
```
