import uuid

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone


class Certificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="certificates")
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="certificates")
    certificate_id = models.CharField(max_length=40, unique=True, db_index=True, editable=False)
    issue_date = models.DateField(default=timezone.localdate, db_index=True)
    pdf_file = models.FileField(
        upload_to="certificates/%Y/%m/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["pdf"])],
    )
    qr_code = models.ImageField(upload_to="certificates/qr/%Y/%m/", blank=True, null=True)
    enrollment = models.OneToOneField(
        "enrollments.Enrollment",
        on_delete=models.CASCADE,
        related_name="certificate",
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["-issue_date"]
        constraints = [
            models.UniqueConstraint(fields=["student", "course"], name="unique_certificate_per_student_course"),
        ]

    @property
    def pdf(self):
        return self.pdf_file

    @property
    def completion_date(self):
        return self.issue_date

    @property
    def issued_at(self):
        return self.issue_date

    def save(self, *args, **kwargs):
        if not self.certificate_id:
            self.certificate_id = f"CERT-{uuid.uuid4().hex[:16].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.certificate_id


class VerificationCode(models.Model):
    certificate = models.OneToOneField(Certificate, on_delete=models.CASCADE, related_name="verification")
    code = models.CharField(max_length=80, unique=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code
