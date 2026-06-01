import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Payment(models.Model):
    class Gateway(models.TextChoices):
        RAZORPAY = "RAZORPAY", "Razorpay"
        STRIPE = "STRIPE", "Stripe"
        PAYPAL = "PAYPAL", "PayPal"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="payments")
    course = models.ForeignKey("courses.Course", on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    gateway = models.CharField(max_length=20, choices=Gateway.choices, default=Gateway.STRIPE)
    payment_status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    transaction_id = models.CharField(max_length=180, blank=True, db_index=True)
    order_id = models.CharField(max_length=180, unique=True, db_index=True)
    currency = models.CharField(max_length=3, default="USD")
    invoice_file = models.FileField(upload_to="invoices/%Y/%m/", blank=True, null=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-payment_date"]
        indexes = [
            models.Index(fields=["student", "payment_status"]),
            models.Index(fields=["gateway", "payment_status"]),
        ]

    @property
    def status(self):
        return self.payment_status

    def __str__(self):
        return f"{self.order_id} - {self.payment_status}"
