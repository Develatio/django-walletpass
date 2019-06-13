import os
import uuid
import hashlib
import json
import tempfile
import secrets
import zipfile
from glob import glob
from django.core.exceptions import ValidationError
from django.utils.module_loading import import_string
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django_walletpass import crypto
from django_walletpass.storage import WalletPassStorage
from django_walletpass.files import WalletpassContentFile
from django_walletpass.settings import dwpconfig as WALLETPASS_CONF


class PassBuilder:
    pass_data = {}
    pass_data_required = {
        "passTypeIdentifier": WALLETPASS_CONF['PASS_TYPE_ID'],
        "serialNumber": None,
        "teamIdentifier": WALLETPASS_CONF['TEAM_ID'],
        "webServiceURL": WALLETPASS_CONF['SERVICE_URL'],
        "authenticationToken": None,
    }
    directory = None
    extra_files = {}
    manifest_dict = {}
    builded_pass_content = None

    def __init__(self, directory=None):
        self.directory = directory
        if directory is not None:
            self._load_pass_json_file_if_exists(directory)
        self.pass_data_required.update({
            "serialNumber": secrets.token_urlsafe(20),
            "authenticationToken": crypto.gen_random_token(),
        })

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
            certcontent=WALLETPASS_CONF['CERT_CONTENT'],
            keycontent=WALLETPASS_CONF['KEY_CONTENT'],
            wwdr_certificate=WALLETPASS_CONF['WWDRCA_CONTENT'],
            data=manifest_json_bytes,
            key_password=WALLETPASS_CONF['KEY_PASSWORD'],
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

    def write_to_model(self, instance=None):
        """Saves the content of builded and zipped pass into Pass model.

        Args:
            instance (Pass, optional): Pass instance, a new one will be created
                if none provided. Defaults to None.

        Returns:
            Pass: instance of Pass (already saved)
        """
        if instance is None:
            instance = Pass()

        setattr(instance, 'pass_type_identifier', WALLETPASS_CONF['PASS_TYPE_ID'])
        setattr(instance, 'serial_number', self.pass_data_required.get('serialNumber'))
        setattr(instance, 'authentication_token', self.pass_data_required.get('authenticationToken'))

        if instance.data.name:
            filename = os.path.basename(instance.data.name)
        else:
            filename = f"{uuid.uuid1()}.pkpass"

        content = WalletpassContentFile(self.builded_pass_content)
        instance.data.delete()
        instance.data.save(filename, content)

        return instance

    def add_file(self, path, content):
        self.extra_files[path] = content


class Pass(models.Model):
    """
    Pass instance
    """
    pass_type_identifier = models.CharField(max_length=150)
    serial_number = models.CharField(max_length=150)
    authentication_token = models.CharField(max_length=150)
    data = models.FileField(
        upload_to=WALLETPASS_CONF['UPLOAD_TO'],
        storage=WalletPassStorage(),
    )
    updated_at = models.DateTimeField(auto_now=True)

    def push_notification(self):
        klass = import_string(WALLETPASS_CONF['WALLETPASS_PUSH_CLASS'])
        push_module = klass()
        for registration in self.registrations.all():
            push_module.push_notification_from_instance(registration)

    def new_pass_builder(self, directory=None):
        builder = PassBuilder(directory)
        builder.pass_data_required.update({
            "passTypeIdentifier": self.pass_type_identifier,
            "serialNumber": self.serial_number,
            "authenticationToken": self.authentication_token,
        })
        return builder

    def get_pass_builder(self):
        builder = PassBuilder()
        with tempfile.TemporaryDirectory() as tmpdirname:
            os.mkdir(os.path.join(tmpdirname, 'data.pass'))
            tmp_pass_dir = os.path.join(tmpdirname, 'data.pass')
            # Put zip file into tmp dir
            zip_path = os.path.join(tmpdirname, 'walletcard.pkpass')
            zip_pkpass = open(zip_path, 'wb')
            zip_pkpass.write(self.data.read())
            zip_pkpass.close()
            # Extract zip file to tmp dir
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(tmp_pass_dir)
            # Populate builder with zip content
            for filepath in glob(os.path.join(tmp_pass_dir, '**'), recursive=True):
                filename = os.path.basename(filepath)
                relative_file_path = os.path.relpath(filepath, tmp_pass_dir)
                if filename == 'pass.json':
                    builder.load_pass_json_file(tmp_pass_dir)
                    continue
                if relative_file_path in ['signature', 'manifest.json', '.', '..']:
                    continue
                if not os.path.isfile(filepath):
                    continue
                builder.add_file(relative_file_path, open(filepath, 'rb').read())
        # Load of these fields due to that those fields are ignored
        # on pass.json loading
        builder.pass_data_required.update({
            "passTypeIdentifier": self.pass_type_identifier,
            "serialNumber": self.serial_number,
            "authenticationToken": self.authentication_token,
        })
        return builder

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
    device_library_identifier = models.CharField(max_length=150)
    push_token = models.CharField(max_length=150)
    pazz = models.ForeignKey(
        Pass,
        on_delete=models.CASCADE,
        related_name='registrations',
    )

    def __unicode__(self):
        return self.device_library_identifier


class Log(models.Model):
    """
    Log message sent by a device
    """
    message = models.TextField()

    def __unicode__(self):
        return self.message
