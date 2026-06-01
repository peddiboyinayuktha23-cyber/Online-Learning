import uuid

from django.conf import settings

from .models import Payment


def create_gateway_order(student, course, gateway=Payment.Gateway.STRIPE):
    return Payment.objects.create(
        student=student,
        course=course,
        amount=course.price,
        gateway=gateway,
        currency=getattr(settings, "PAYMENT_CURRENCY", "USD"),
        order_id=f"ORD-{uuid.uuid4().hex[:18].upper()}",
    )


def verify_gateway_payment(payment, transaction_id, gateway_response=None):
    payment.transaction_id = transaction_id
    payment.gateway_response = gateway_response or {}
    payment.payment_status = Payment.Status.SUCCESS
    payment.save(update_fields=["transaction_id", "gateway_response", "payment_status", "updated_at"])
    return payment
