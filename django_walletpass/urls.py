from django.urls import re_path
from . import classviews

urlpatterns = [
    re_path(
        r'^v1/devices/(?P<device_library_id>.+)/registrations/(?P<pass_type_id>.+)/(?P<serial_number>.+)$',
        classviews.RegisterPassViewSet.as_view({
            'post': 'create',
            'delete': 'destroy',
        }),
        name='walletpass_register_pass',
    ),
    re_path(
        r'^v1/devices/(?P<device_library_id>.+)/registrations/(?P<pass_type_id>.+)$',
        classviews.RegistrationsViewSet.as_view({
            'get': 'list',
        }),
        name='walletpass_registrations',
    ),
    re_path(
        r'^v1/passes/(?P<pass_type_id>.+)/(?P<serial_number>.+)$',
        classviews.LatestVersionViewSet.as_view({
            'get': 'retrieve'
        }),
        name='walletpass_latest_version',
    ),
    re_path(
        r'^v1/log$',
        classviews.LogViewSet.as_view({
            'post': 'create',
        }),
        name='walletpass_log',
    ),
]
