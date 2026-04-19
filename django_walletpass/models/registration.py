from django.db import models


class Registration(models.Model):
    """
    Registration of a Pass on a device
    """
    device_library_identifier = models.CharField(max_length=150)
    push_token = models.TextField()
    pazz = models.ForeignKey(
        "Pass",
        on_delete=models.CASCADE,
        related_name='registrations',
    )

    def __unicode__(self):
        return self.device_library_identifier

    def __str__(self):
        return str(self.device_library_identifier)
