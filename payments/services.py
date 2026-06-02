import uuid

from django.conf import settings
from django.urls import reverse

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


def create_stripe_checkout_session(request, payment):
    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    success_url = request.build_absolute_uri(reverse("payment_success", kwargs={"payment_id": payment.id}))
    cancel_url = request.build_absolute_uri(reverse("payment_failure", kwargs={"payment_id": payment.id}))
    return stripe.checkout.Session.create(
        mode="payment",
        client_reference_id=str(payment.id),
        line_items=[
            {
                "price_data": {
                    "currency": payment.currency.lower(),
                    "product_data": {"name": payment.course.title},
                    "unit_amount": int(payment.amount * 100),
                },
                "quantity": 1,
            }
        ],
        success_url=success_url,
        cancel_url=cancel_url,
    )
