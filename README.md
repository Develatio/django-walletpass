![PyPI](https://img.shields.io/pypi/v/django-walletpass.svg)
![t](https://img.shields.io/badge/status-beta-red.svg)


# django-walletpass


This application implements the creation of **signed .pkpass** files and
**API endpoints** for pass registration, updates and logging.

## Features

- Build .pkpass with the `PassBuilder` class
- Sign .pkpass with SMIME (as apple describes in their documentation)
- Server implementation for store, registration, update and logging
- Push notifications (APNs) on pass update
- Individual storage backend setting
- Support for mime-type upload using django-storages S3

## Requirements

- Django 2.*
- python >= 3.5
- pyca/cryptography (for .pkpass SMIME sign)

## Getting Started

### Install

```
$ pip install django-walletpass
```

### Configure

Add 'django_walletpass' to you installed apps in the settings.py file.

Load the content of your cert.pem and key.pem in your settings.py file.

```

WALLETPASS = {
    'CERT_PATH': 'path/to/your/cert.pem',
    'KEY_PATH': 'path/to/your/key.pem',
    # (None if isn't protected)
    # MUST be in bytes-like
    'KEY_PASSWORD': b'1234',
}
```

Add extra needed conf to your settings.py file.

```
WALLETPASS = {
    'CERT_PATH': 'path/to/your/cert.pem',
    'KEY_PATH': 'path/to/your/key.pem',
    # (None if isn't protected)
    # MUST be in bytes-like
    'KEY_PASSWORD': b'1234',

    'PASS_TYPE_ID': 'pass.io.develat.devpubs.example',
    'TEAM_ID': '123456',
    'SERVICE_URL': 'https://example.com/passes/',
}
```

You should also import the urls into your site urls.
```
urlpatterns = [
    url(r'^api/passes/', include('django_walletpass.urls')),
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


### Configure storage and upload path (optional)

```
WALLETPASS_CONF = {
    # Defaults to DEFAULT_FILE_STORAGE
    'STORAGE_CLASS': 'my.custom.storageclass,
    'UPLOAD_TO': 'passes'
}
```

### Push notifications sandbox (optional)

```
WALLETPASS_CONF = {
    'PUSH_SANDBOX': False,
}
```

### CA certificates path (optional)

```
WALLETPASS_CONF = {
    # Cert in der format.
    'APPLE_WWDRCA_CERT_PATH': 'path/to/cert.cer',
    # Cert in pem format.
    'APPLE_WWDRCA_PEM_PATH': 'path/to/cert.pem',
}
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
    "passTypeIdentifier": WALLETPASS_CONF['PASS_TYPE_ID'],
    "serialNumber": secrets.token_urlsafe(20),
    "teamIdentifier": WALLETPASS_CONF['TEAM_ID'],
    "webServiceURL": WALLETPASS_CONF['SERVICE_URL'],
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

Save to new record in DB:

```
pass_instance = builder.write_to_model()
pass_instance.save()
```

Save to existent record in DB:

```
builder.write_to_model(pass_instance)
pass_instance.save()
```

### Load .pkpass from DB and update

```
builder = pass_instance.get_pass_builder()
builder.pass_data.update({'field': 'value'})
builder.build()
builder.save_to_db(pass_instance)
```
