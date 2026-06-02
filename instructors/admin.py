from django.contrib import admin

from .models import InstructorPayout


@admin.register(InstructorPayout)
class InstructorPayoutAdmin(admin.ModelAdmin):
    list_display = ("instructor", "amount", "status", "reference", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("instructor__email", "reference")
    autocomplete_fields = ("instructor",)
