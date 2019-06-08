from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        r'^v1/devices/(?P<device_library_id>.+)/registrations/(?P<pass_type_id>[\w\.\d]+)/(?P<serial_number>.+)$',
        views.register_pass,
        name='walletpass_register',
    ),
    url(
        r'^v1/devices/(?P<device_library_id>.+)/registrations/(?P<pass_type_id>[\w\.\d]+)$',
        views.registrations,
        'walletpass_registrations',
    ),
    url(
        r'^v1/passes/(?P<pass_type_id>[\w\.\d]+)/(?P<serial_number>.+)$',
        views.latest_version,
        'walletpass_passes',
    ),
    url(
        r'^v1/log$',
        views.log,
    ),
]
