from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from django_walletpass.models import Pass, Registration, Log

admin.site.register(Pass)
admin.site.register(Registration)


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "status",
        "task_type",
        # "pass_type_identifier",
        # "serial_number",
        "pass_",
        # "web_service_url",
        "device_id",
        "msg",
    )
    list_filter = ("status", "task_type", "pass_type_identifier")
    search_fields = ("pass_type_identifier", "serial_number", "device_id", "msg", "message")
    readonly_fields = ("created_at", "pass_")
    raw_id_fields = ("pazz",)
    list_select_related = ("pazz",)

    def pass_(self, obj: Log):
        if obj.pazz_id:
            url = reverse(
                "admin:%s_%s_change" % (obj.pazz._meta.app_label, obj.pazz._meta.model_name),
                args=[obj.pazz_id],
            )
            return format_html(
                "<a href='{url}'>{title}</a>",
                url=url,
                title=obj.serial_number,
            )
        return obj.serial_number

    pass_.short_description = "Pass"
