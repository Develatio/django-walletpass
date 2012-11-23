from django.db import models


class Pass(models.Model):
    pass_type_identifier = models.CharField(max_length=50)
    serial_number = models.CharField(max_length=50)
    authentication_token = models.CharField(max_length=50)

    def __unicode__(self):
        return self.serial_number


class Registration(models.Model):
    device_library_identifier = models.CharField(max_length=50)
    push_token = models.CharField(max_length=50)
    pazz = models.ForeignKey(Pass)

    def __unicode__(self):
        return self.device_library_identifier