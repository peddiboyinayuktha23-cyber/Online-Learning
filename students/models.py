import uuid

from django.conf import settings
from django.db import models

from onlinelearning.core_models import AuditModel


class StudentNote(AuditModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_notes")
    title = models.CharField(max_length=180)
    body = models.TextField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student}: {self.title}"
