import os
import hashlib
import json
import tempfile
import secrets
import zipfile
from glob import glob
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_walletpass import settings as dwp_settings
from django_walletpass import crypto


class PassBuilder:
    pass_data = {}
    pass_data_required = {
        "passTypeIdentifier": settings.WALLETPASS_PASS_TYPE_ID,
        "serialNumber": secrets.token_urlsafe(20),
        "teamIdentifier": settings.WALLETPASS_TEAM_ID,
        "webServiceURL": settings.WALLETPASS_SERVICE_URL,
        "authenticationToken": crypto.gen_random_token(),
    }
    directory = None
    extra_files = {}
    manifest_dict = {}
    builded_pass_content = None

    def __init__(self, directory=None):
        self.directory = directory
        if directory is not None:
            self._load_pass_json_file_if_exists(directory)

    def _copy_dir_files(self, tmp_pass_dir):
        """Copy files from provided base dir to temporal dir

        Args:
            tmp_pass_dir (str): temporal dir path
        """
        for absolute_filepath in glob(os.path.join(self.directory, '**'), recursive=True):
            filename = os.path.basename(absolute_filepath)
            relative_file_path = os.path.relpath(absolute_filepath, self.directory)
            if filename == '.DS_Store':
                continue
            if not os.path.isfile(absolute_filepath):
                continue
            filecontent = open(absolute_filepath, 'rb').read()
            # Add files to manifest
            self.manifest_dict[relative_file_path] = hashlib.sha1(filecontent).hexdigest()
            dest_abs_filepath = os.path.join(tmp_pass_dir, relative_file_path)
            dest_abs_dirpath = os.path.dirname(dest_abs_filepath)
            if not os.path.exists(dest_abs_dirpath):
                os.makedirs(dest_abs_dirpath)
            ff = open(dest_abs_filepath, 'wb')
            ff.write(filecontent)
            ff.close()

    def _write_extra_files(self, tmp_pass_dir):
        """Write extra files contained in self.extra_files into tmp dir

        Args:
            tmp_pass_dir (str): temporal dir path
        """
        for relative_file_path, filecontent in self.extra_files.items():
            # Add files to manifest
            self.manifest_dict[relative_file_path] = hashlib.sha1(filecontent).hexdigest()
            dest_abs_filepath = os.path.join(tmp_pass_dir, relative_file_path)
            dest_abs_dirpath = os.path.dirname(dest_abs_filepath)
            if not os.path.exists(dest_abs_dirpath):
                os.makedirs(dest_abs_dirpath)
            ff = open(dest_abs_filepath, 'wb')
            ff.write(filecontent)
            ff.close()

    def _write_pass_json(self, tmp_pass_dir):
        """Write content of self.pass_data to pass.json (in JSON format)

        Args:
            tmp_pass_dir (str): temporal dir path where pass.json will be saved
        """
        pass_json = json.dumps(self.pass_data)
        pass_json_bytes = bytes(pass_json, 'utf8')
        # Add pass.json to manifest
        self.manifest_dict['pass.json'] = hashlib.sha1(pass_json_bytes).hexdigest()
        ff = open(os.path.join(tmp_pass_dir, 'pass.json'), 'wb')
        ff.write(pass_json_bytes)
        ff.close()

    def _write_manifest_json_and_signature(self, tmp_pass_dir):
        """Write the content of self.manifest_dict into manifest.json

        Args:
            tmp_pass_dir (str): temporal dir path
        """
        manifest_json = json.dumps(self.manifest_dict)
        manifest_json_bytes = bytes(manifest_json, 'utf8')
        ff = open(os.path.join(tmp_pass_dir, 'manifest.json'), 'wb')
        ff.write(manifest_json_bytes)
        ff.close()
        signature_content = crypto.pkcs7_sign(
            settings.WALLETPASS_CERTIFICATES_P12,
            dwp_settings.APPLE_WWDRCA_CERT,
            manifest_json_bytes,
            settings.WALLETPASS_CERTIFICATES_P12_PASSWORD,
        )
        ff = open(os.path.join(tmp_pass_dir, 'signature'), 'wb')
        ff.write(signature_content)
        ff.close()

    def _zip_all(self, directory):
        zip_file_path = os.path.join(directory, '..', 'walletcard.pkpass')
        zip_pkpass = zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)
        for filepath in glob(os.path.join(directory, '**'), recursive=True):
            relative_file_path = os.path.relpath(filepath, directory)
            zip_pkpass.write(filepath, arcname=relative_file_path)
        zip_pkpass.close()
        return open(zip_file_path, 'rb').read()

    def _load_pass_json_file_if_exists(self, directory):
        """Call self.load_pass_json_file if pass.json exist

        Args:
            directory (str): directory where pass.json resides
        """
        if os.path.isfile(os.path.join(directory, 'pass.json')):
            self.load_pass_json_file(directory)

    def _clean_manifest(self):
        self.manifest_dict = {}

    def _clean_builded_pass_content(self):
        self.builded_pass_content = None

    def validate(self):
        """Some validations before build the .pkpass file

        Raises:
            ValidationError: on validation error
        """
        if not self.pass_data:
            raise ValidationError(_("Cannot obtain data for pass.json."))

    def clean(self):
        self._clean_manifest()
        self._clean_builded_pass_content()
        self.validate()

    def load_pass_json_file(self, dir):
        """Load json file without test if exists.

        Args:
            dir (str): path where resides the pass.json
        """
        json_data = open(os.path.join(dir, 'pass.json'), 'r').read()
        self.pass_data = json.loads(json_data)

    def pre_build_pass_data(self):
        """Update self.pass_data with self.pass_data_required content
        """
        self.pass_data.update(self.pass_data_required)

    def build(self):
        """Build .pkpass file
        """
        self.clean()
        with tempfile.TemporaryDirectory() as tmpdirname:
            os.mkdir(os.path.join(tmpdirname, 'data.pass'))
            tmp_pass_dir = os.path.join(tmpdirname, 'data.pass')
            if self.directory:
                self._copy_dir_files(tmp_pass_dir)
            self._write_extra_files(tmp_pass_dir)
            self.pre_build_pass_data()
            self._write_pass_json(tmp_pass_dir)
            self._write_manifest_json_and_signature(tmp_pass_dir)
            self.builded_pass_content = self._zip_all(tmp_pass_dir)
        return self.builded_pass_content

    def add_file(self, path, content):
        self.extra_files[path] = content


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
