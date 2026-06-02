from io import BytesIO

from django.core.files.base import ContentFile
from django.urls import reverse
from django.utils import timezone
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas

from .models import Certificate


def generate_certificate_pdf(certificate: Certificate):
    buffer = BytesIO()
    page = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)
    student_name = certificate.student.full_name
    instructor_name = certificate.course.instructor.full_name

    page.setFont("Helvetica-Bold", 28)
    page.drawCentredString(width / 2, height - 120, "Certificate of Completion")
    page.setFont("Helvetica", 16)
    page.drawCentredString(width / 2, height - 180, "This certifies that")
    page.setFont("Helvetica-Bold", 24)
    page.drawCentredString(width / 2, height - 230, student_name)
    page.setFont("Helvetica", 16)
    page.drawCentredString(width / 2, height - 280, "successfully completed")
    page.setFont("Helvetica-Bold", 22)
    page.drawCentredString(width / 2, height - 330, certificate.course.title)
    page.setFont("Helvetica", 12)
    page.drawString(100, 110, f"Instructor: {instructor_name}")
    page.drawString(100, 90, f"Certificate ID: {certificate.certificate_id}")
    page.drawString(100, 70, f"Completion Date: {certificate.issue_date or timezone.localdate()}")
    page.showPage()
    page.save()

    filename = f"{certificate.certificate_id}.pdf"
    certificate.pdf_file.save(filename, ContentFile(buffer.getvalue()), save=True)
    return certificate


def generate_certificate_qr(certificate: Certificate, request=None):
    try:
        import qrcode
    except ImportError:
        return certificate

    path = reverse("verify_certificate", kwargs={"certificate_id": certificate.certificate_id})
    verify_url = request.build_absolute_uri(path) if request else path
    image = qrcode.make(verify_url)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    certificate.qr_code.save(f"{certificate.certificate_id}.png", ContentFile(buffer.getvalue()), save=True)
    return certificate
