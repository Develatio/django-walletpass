import os
import hashlib
import json
import tempfile
import secrets
from glob import glob
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_walletpass import settings as dwp_settings
from django_walletpass import crypto


class PassBuilder:
    pass_data = {}
    directory = None
    extra_files = {}
    manifest_dict = {}
    manifest_json = None

    def __init__(self, directory=None):
        self.directory = directory
        if directory is not None and os.path.isfile(os.path.join(directory, 'pass.json')):
            json_data = open(os.path.join(directory, 'pass.json'), 'r').read()
            self.pass_data = json.loads(json_data)

    # TODO: handle directories
    def _copy_dir_files(self, tmp_pass_dir):
        for filepath in glob(os.path.join(self.directory, '**')):
            filename = os.path.basename(filepath)
            if filename == '.DS_Store':
                continue
            filecontent = open(filepath, 'rb').read()
            self.manifest_dict[filename] = hashlib.sha1(filecontent).hexdigest()
            ff = open(os.path.join(tmp_pass_dir, filename), 'wb')
            ff.write(filecontent)
            ff.close()

    def _write_extra_files(self, tmp_pass_dir):
        for filename, filecontent in self.extra_files:
            self.manifest_dict[filename] = hashlib.sha1(filecontent).hexdigest()
            ff = open(os.path.join(tmp_pass_dir, filename), 'wb')
            ff.write(filecontent)
            ff.close()

    def _write_pass_json(self, tmp_pass_dir):
        self.pass_data.update({
            "passTypeIdentifier": settings.WALLETPASS_PASS_TYPE_ID,
            "serialNumber": secrets.token_urlsafe(20),
            "teamIdentifier": settings.WALLETPASS_TEAM_ID,
            "webServiceURL": settings.WALLETPASS_SERVICE_URL,
            "authenticationToken": crypto.gen_random_token(),
        })
        pass_json = json.dumps(self.pass_data)
        self.manifest_dict['pass.json'] = hashlib.sha1(pass_json).hexdigest()
        ff = open(os.path.join(tmp_pass_dir, 'pass.json'), 'w')
        ff.write(pass_json)
        ff.close()

    def _write_manifest_json(self, tmp_pass_dir):
        self.manifest_json = json.dumps(self.manifest_dict)
        ff = open(os.path.join(tmp_pass_dir, 'manifest.json'), 'w')
        ff.write(self.manifest_json)
        ff.close()

    def _write_signature(self, tmp_pass_dir):
        signature_content = crypto.pkcs7_sign(
            settings.WALLETPASS_CERTIFICATES_P12,
            dwp_settings.APPLE_WWDRCA_CERT,
            bytes(self.manifest_json, 'utf8'),
            settings.WALLETPASS_CERTIFICATES_P12_PASSWORD,
        )
        ff = open(os.path.join(tmp_pass_dir, 'signature'), 'wb')
        ff.write(self.signature_content)
        ff.close()

    def validate(self):
        if not self.pass_data:
            raise ValidationError(_("Cannot obtain data for pass.json."))

    def clean(self):
        self.manifest_dict = {}
        self.manifest_json = None

    def build(self):
        self.clean()
        self.validate()
        self.manifest_dict = {}
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmp_pass_dir = os.mkdir(os.path.join(tmpdirname, 'data.pkpass'))
            self._copy_dir_files(tmp_pass_dir)
            self._write_extra_files(tmp_pass_dir)
            self._write_pass_json(tmp_pass_dir)
            self._write_manifest_json(tmp_pass_dir)
            self._write_signature(tmp_pass_dir)

    def add_file(name, content):
        self.extra_files[name] = content


class Pass(models.Model):
    """
    Pass instance
    """
    pass_type_identifier = models.CharField(max_length=50)
    serial_number = models.CharField(max_length=50)
    authentication_token = models.CharField(max_length=50)
    data = models.FileField(upload_to='passes')
    updated_at = models.DateTimeField()

    def __unicode__(self):
        return self.serial_number

    class Meta:
        verbose_name_plural = "passes"
        unique_together = (
            'pass_type_identifier',
            'serial_number',
        ),


class Registration(models.Model):
    """
    Registration of a Pass on a device
    """
    device_library_identifier = models.CharField(max_length=50)
    push_token = models.CharField(max_length=50)
    pazz = models.ForeignKey(Pass, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.device_library_identifier


class Log(models.Model):
    """
    Log message sent by a device
    """
    message = models.TextField()

    def __unicode__(self):
        return self.message
