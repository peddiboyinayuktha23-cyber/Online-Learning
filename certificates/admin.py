from django.contrib import admin

from .models import Certificate, VerificationCode


class VerificationCodeInline(admin.StackedInline):
    model = VerificationCode
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("certificate_id", "student", "course", "issue_date")
    list_filter = ("issue_date",)
    search_fields = ("certificate_id", "student__email", "course__title")
    autocomplete_fields = ("student", "course", "enrollment")
    readonly_fields = ("certificate_id",)
    inlines = [VerificationCodeInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("student", "course", "enrollment")


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "certificate", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("code", "certificate__certificate_id")
    autocomplete_fields = ("certificate",)
    readonly_fields = ("created_at",)
