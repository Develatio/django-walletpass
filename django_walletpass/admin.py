from django.contrib import admin
from django_walletpass.models import Pass, Registration, Log
# from django_walletpass import settings
# from apns import APNs, Payload

# TODO: Implement push
# def push_update(modeladmin, request, queryset):
#     for r in queryset.all():
#         # TODO: use different certificates for different stores
#         apns = APNs(use_sandbox=False,
#                     cert_file=settings.WALLETPASS_CERT,
#                     key_file=settings.WALLETPASS_CERT_KEY)
#         apns.gateway_server.send_notification(r.push_token, Payload())

# push_update.short_description = "Send a push notification to update Pass"

# class RegistrationAdmin(admin.ModelAdmin):
#     actions = [push_update]

admin.site.register(Pass)
admin.site.register(Registration)
admin.site.register(Log)
