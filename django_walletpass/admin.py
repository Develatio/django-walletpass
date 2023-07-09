from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from django_walletpass.models import Pass, Registration, Log


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


@admin.register(Pass)
class PassAdmin(admin.ModelAdmin):
    list_display = ("serial_number", "updated_at", "pass_type_identifier", "wallet_pass_")
    search_fields = ("serial_number", "pass_type_identifier", "authentication_token", "data")
    list_filter = ("pass_type_identifier", "updated_at")
    date_hierarchy = "updated_at"
    readonly_fields = ("wallet_pass_", "updated_at")

    def wallet_pass_(self, obj: Pass):
        if obj.data:
            svg_icon = '<svg width="13" height="16" viewBox="0 0 13 16" fill="none" xmlns="http://www.w3.org/2000/svg">' \
                       '<path d="M2.86133 15.3926C2.15495 15.3926 1.62402 15.2126 1.26855 14.8525C0.917643 14.4971 0.742188 13.9639 0.742188 13.2529V2.88281C0.742188 2.16732 0.917643 1.63184 1.26855 1.27637C1.62402 0.916341 2.15495 0.736328 2.86133 0.736328H4.88477C5.13997 0.736328 5.26758 0.873047 5.26758 1.14648C5.26758 1.50195 5.37923 1.79362 5.60254 2.02148C5.8304 2.24479 6.12663 2.35645 6.49121 2.35645C6.85579 2.35645 7.14974 2.24479 7.37305 2.02148C7.59635 1.79362 7.70801 1.50195 7.70801 1.14648C7.70801 0.873047 7.83561 0.736328 8.09082 0.736328H10.1211C10.8275 0.736328 11.3561 0.916341 11.707 1.27637C12.0625 1.63184 12.2402 2.16732 12.2402 2.88281V13.2529C12.2402 13.9639 12.0625 14.4971 11.707 14.8525C11.3561 15.2126 10.8275 15.3926 10.1211 15.3926H2.86133ZM2.91602 14.292H10.0664C10.4219 14.292 10.6885 14.1986 10.8662 14.0117C11.0485 13.8294 11.1396 13.5697 11.1396 13.2324V2.90332C11.1396 2.56152 11.0485 2.29948 10.8662 2.11719C10.6885 1.93034 10.4219 1.83691 10.0664 1.83691H8.11816L8.76074 1.44727C8.69694 2.04427 8.45768 2.52279 8.04297 2.88281C7.63281 3.24284 7.11556 3.42285 6.49121 3.42285C5.86686 3.42285 5.34733 3.24284 4.93262 2.88281C4.52246 2.52279 4.28776 2.04427 4.22852 1.44727L4.86426 1.83691H2.91602C2.56055 1.83691 2.29167 1.93034 2.10938 2.11719C1.93164 2.29948 1.84277 2.56152 1.84277 2.90332V13.2324C1.84277 13.5697 1.93164 13.8294 2.10938 14.0117C2.29167 14.1986 2.56055 14.292 2.91602 14.292ZM3.90039 5.8291C3.77734 5.8291 3.6748 5.78809 3.59277 5.70605C3.5153 5.62402 3.47656 5.52148 3.47656 5.39844C3.47656 5.27995 3.5153 5.18197 3.59277 5.10449C3.6748 5.02246 3.77734 4.98145 3.90039 4.98145H9.08887C9.20736 4.98145 9.30534 5.02246 9.38281 5.10449C9.46484 5.18197 9.50586 5.27995 9.50586 5.39844C9.50586 5.52148 9.46484 5.62402 9.38281 5.70605C9.30534 5.78809 9.20736 5.8291 9.08887 5.8291H3.90039ZM3.90039 8.25586C3.77734 8.25586 3.6748 8.21712 3.59277 8.13965C3.5153 8.05762 3.47656 7.95736 3.47656 7.83887C3.47656 7.72038 3.5153 7.62012 3.59277 7.53809C3.6748 7.45605 3.77734 7.41504 3.90039 7.41504H6.35449C6.47754 7.41504 6.5778 7.45605 6.65527 7.53809C6.7373 7.62012 6.77832 7.72038 6.77832 7.83887C6.77832 7.95736 6.7373 8.05762 6.65527 8.13965C6.5778 8.21712 6.47754 8.25586 6.35449 8.25586H3.90039Z" fill="black"/>' \
                       '</svg>'
            return format_html(
                "<a href='{url}' alt='{title}'>{icon}</a>",
                url=obj.data.url,
                title=obj.data.name,
                icon=mark_safe(svg_icon),
            )
        return

    wallet_pass_.short_description = "Pass"


@admin.register(Registration)
class PassAdmin(admin.ModelAdmin):
    list_display = ("device_library_identifier", "push_token", "pass_")
    search_fields = ("device_library_identifier", "push_token", "pazz")
    raw_id_fields = ("pazz",)
    readonly_fields = ("pass_",)

    def pass_(self, obj: Registration):
        if obj.pazz_id:
            url = reverse(
                "admin:%s_%s_change" % (obj.pazz._meta.app_label, obj.pazz._meta.model_name),
                args=[obj.pazz_id],
            )
            return format_html(
                "<a href='{url}'>{title}</a>",
                url=url,
                title=obj.pazz.serial_number,
            )
        return

    pass_.short_description = "Pass"
