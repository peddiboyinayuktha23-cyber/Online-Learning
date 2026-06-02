from django.shortcuts import get_object_or_404, render

from .models import Certificate


def certificate_detail(request, certificate_id):
    certificate = get_object_or_404(Certificate.objects.select_related("student", "course"), certificate_id=certificate_id)
    return render(request, "certificates/certificate_detail.html", {"certificate": certificate})


def verify_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate.objects.select_related("student", "course"), certificate_id=certificate_id)
    return render(request, "certificates/verify.html", {"certificate": certificate, "is_valid": True})
