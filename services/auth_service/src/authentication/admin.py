from django.contrib import admin

from .models import OTPRequest


@admin.register(OTPRequest)
class OTPRequestAdmin(admin.ModelAdmin):
    list_display = ("email", "expires_at", "attempts", "created_at")
    search_fields = ("email",)
    readonly_fields = ("created_at", "last_sent_at")

