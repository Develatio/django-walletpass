import re

from dateutil.parser import parse as datetime_parse
from django.db import models
from django.utils import timezone

from django_walletpass.models import Pass

# pylint: disable=line-too-long
PATTERN_REGISTER = r"\[(.*?)\]\s(.*?)\s\(for device (.*?), pass type (.*?), serial number (.*?); with web service url (.*?)\)\s(.*?): (.*$)"
PATTERN_GET = r"\[(.*?)\]\s(.*?)\s\(pass type (.*?), serial number (.*?), if-modified-since \(.*?\); with web service url (.*?)\) (.*?): (.*$)"
PATTERN_WEB_SERVICE_ERROR = r"\[(.*?)\]\s(.*?)\sfor (.*?)\s\((.*?)\):\s(.*$)"
PATTERN_GET_WARNING = r"\[(.*?)\]\s(.*?)\s\(pass type (.*?), serial number (.*?), if-modified-since \(.*?\); with web service url (.*?)\) (.*?): (.*\.)\s(.*$)"
# pylint: disable=line-too-long

class Log(models.Model):
    """
    Log message sent by a device
    """
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=100, null=True, blank=True)
    task_type = models.CharField(max_length=255, null=True, blank=True)
    pass_type_identifier = models.CharField(max_length=255, null=True, blank=True)
    serial_number = models.CharField(max_length=255, null=True, blank=True)
    pazz = models.ForeignKey("Pass", null=True, blank=True, on_delete=models.CASCADE, related_name='logs')
    web_service_url = models.URLField(null=True, blank=True)
    device_id = models.CharField(max_length=255, null=True, blank=True)
    msg = models.TextField(null=True, blank=True)
    message = models.TextField()

    def __unicode__(self):
        return self.message

    def __str__(self):
        return self.created_at.strftime('%d/%m/%y %H:%M:%S')

    @classmethod
    def parse_log(cls, log, message):
        match_register = re.match(PATTERN_REGISTER, message)
        match_get = re.match(PATTERN_GET, message)
        match_web_service_error = re.match(PATTERN_WEB_SERVICE_ERROR, message)
        match_get_warning = re.match(PATTERN_GET_WARNING, message)

        if match_register:
            timestamp_str, task_type, device_id, pass_type_identifier, serial_number, web_service_url, status, msg = match_register.groups()
        elif match_get:
            timestamp_str, task_type, pass_type_identifier, serial_number, web_service_url, status, msg = match_get.groups()
            device_id = None  # 'Get pass task' entries don't include device_id
        elif match_web_service_error:
            timestamp_str, task_type, pass_type_identifier, web_service_url, msg = match_web_service_error.groups()
            serial_number = None
            device_id = None
            status = "error"
        elif match_get_warning:
            timestamp_str, task_type, pass_type_identifier, serial_number, web_service_url, status, msg = match_get_warning.groups()
            device_id = None
            status = "warning"
        else:
            log.status = 'unknown'
            log.message = message
            log.save()
            return  # Log entry didn't match any known pattern

        if 'error' in status:
            status = 'error'
        elif 'warning' in status:
            status = 'warning'

        log.created_at = datetime_parse(timestamp_str)
        log.status = status
        log.task_type = task_type
        log.device_id = device_id
        log.pass_type_identifier = pass_type_identifier
        log.serial_number = serial_number
        log.web_service_url = web_service_url
        log.msg = msg
        log.message = message

        if serial_number:
            try:
                pazz = Pass.objects.get(serial_number=serial_number)
                log.pazz = pazz
            except Pass.DoesNotExist:
                pass

        log.save()

        log.save()
