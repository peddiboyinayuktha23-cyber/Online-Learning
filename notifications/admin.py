from django.contrib import admin

from .models import EmailNotification, Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "notification_type", "title", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("user__email", "title", "message")
    autocomplete_fields = ("user",)


@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "subject", "status", "sent_at", "created_at")
    list_filter = ("status", "sent_at", "created_at")
    search_fields = ("user__email", "subject")
    autocomplete_fields = ("user",)
