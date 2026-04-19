import os
import tempfile
import zipfile
from glob import glob

from django.db import models
from django.utils.module_loading import import_string

from django_walletpass.settings import dwpconfig as WALLETPASS_CONF
from django_walletpass.storage import WalletPassStorage


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

    def get_registrations(self):
        return self.registrations.all()

    def push_notification(self):
        klass = import_string(WALLETPASS_CONF['WALLETPASS_PUSH_CLASS'])
        push_module = klass()
        for registration in self.get_registrations():
            response = push_module.push_notification_from_instance(registration)
            # delete invalid registration
            if response.status == '410':
                registration.delete()

    def new_pass_builder(self, directory=None):
        from django_walletpass.services import PassBuilder

        builder = PassBuilder(directory)
        builder.pass_data_required.update({
            "passTypeIdentifier": self.pass_type_identifier,
            "serialNumber": self.serial_number,
            "authenticationToken": self.authentication_token,
        })
        return builder

    def get_pass_builder(self):
        from django_walletpass.services import PassBuilder

        builder = PassBuilder()
        with tempfile.TemporaryDirectory() as tmpdirname:
            os.mkdir(os.path.join(tmpdirname, 'data.pass'))
            tmp_pass_dir = os.path.join(tmpdirname, 'data.pass')
            # Put zip file into tmp dir
            zip_path = os.path.join(tmpdirname, 'walletcard.pkpass')
            with open(zip_path, 'wb') as ffile:
                self.data.seek(0)
                ffile.write(self.data.read())

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
                with open(filepath, 'rb') as ffile:
                    builder.add_file(relative_file_path, ffile.read())
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

    def __str__(self):
        return str(self.serial_number)

    class Meta:
        verbose_name_plural = "passes"
        unique_together = (
            'pass_type_identifier',
            'serial_number',
        )
