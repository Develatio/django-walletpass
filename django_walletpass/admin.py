from django.contrib import admin
from django.template import Context, Template
from django.urls import reverse
from django.utils.html import format_html

from django_walletpass.models import Log, Pass, Registration


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
    search_fields = (
        "pass_type_identifier",
        "serial_number",
        "device_id",
        "msg",
        "message",
    )
    readonly_fields = ("created_at", "pass_")
    raw_id_fields = ("pazz",)
    list_select_related = ("pazz",)

    def pass_(self, obj: Log):
        if obj.pazz_id:
            # pylint: disable=protected-access
            url = reverse(
                f"admin:{obj.pazz._meta.app_label}_{obj.pazz._meta.model_name}_change",
                args=[obj.pazz_id],
            )
            # pylint: enable=protected-access
            return format_html(
                "<a href='{url}'>{title}</a>",
                url=url,
                title=obj.serial_number,
            )
        return obj.serial_number

    pass_.short_description = "Pass"


@admin.register(Pass)
class PassAdmin(admin.ModelAdmin):
    list_display = (
        "serial_number",
        "updated_at",
        "pass_type_identifier",
        "wallet_pass_",
    )
    search_fields = (
        "serial_number",
        "pass_type_identifier",
        "authentication_token",
        "data",
    )
    list_filter = ("pass_type_identifier", "updated_at")
    date_hierarchy = "updated_at"
    readonly_fields = ("wallet_pass_", "updated_at")

    def wallet_pass_(self, obj: Pass):
        if obj.data:
            return format_html(
                Template('''
                    {% load static %}
                    <a href='{url}' alt='{title}'>
                        <img src='{% static 'admin/passbook_icon.svg' %}'/>
                    </a>
                ''').render(Context({})),
                url=obj.data.url,
                title=obj.data.name,
            )
        return ""

    wallet_pass_.short_description = "Pass"


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("device_library_identifier", "push_token", "pass_")
    search_fields = ("device_library_identifier", "push_token", "pazz__serial_number")
    raw_id_fields = ("pazz",)
    readonly_fields = ("pass_",)

    def pass_(self, obj: Registration):
        if obj.pazz_id:
            # pylint: disable=protected-access
            url = reverse(
                f"admin:{obj.pazz._meta.app_label}_{obj.pazz._meta.model_name}_change",
                args=[obj.pazz_id],
            )
            # pylint: enable=protected-access
            return format_html(
                "<a href='{url}'>{title}</a>",
                url=url,
                title=obj.pazz.serial_number,
            )
        return ""

    pass_.short_description = "Pass"
