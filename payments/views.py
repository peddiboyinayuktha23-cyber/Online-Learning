from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from courses.models import Course

from .models import Payment
from .services import create_gateway_order, create_stripe_checkout_session


@login_required
def checkout(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    payment = create_gateway_order(request.user, course, Payment.Gateway.STRIPE)
    if request.method == "POST":
        session = create_stripe_checkout_session(request, payment)
        return redirect(session.url)
    return render(request, "payments/checkout.html", {"course": course, "payment": payment})


def payment_success(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    payment.payment_status = Payment.Status.SUCCESS
    payment.save(update_fields=["payment_status", "updated_at"])
    return render(request, "payments/success.html", {"payment": payment})


def payment_failure(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    payment.payment_status = Payment.Status.FAILED
    payment.save(update_fields=["payment_status", "updated_at"])
    return render(request, "payments/failure.html", {"payment": payment})
