from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order_id", "student", "course", "amount", "gateway", "payment_status", "payment_date")
    list_filter = ("gateway", "payment_status", "currency", "payment_date")
    search_fields = ("order_id", "transaction_id", "student__email", "course__title")
    autocomplete_fields = ("student", "course")
    readonly_fields = ("payment_date", "updated_at")
