from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Type(models.TextChoices):
        COURSE = "COURSE", "Course"
        ASSIGNMENT = "ASSIGNMENT", "Assignment"
        QUIZ = "QUIZ", "Quiz"
        PAYMENT = "PAYMENT", "Payment"
        CERTIFICATE = "CERTIFICATE", "Certificate"
        SYSTEM = "SYSTEM", "System"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=20, choices=Type.choices, default=Type.SYSTEM)
    title = models.CharField(max_length=180)
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["notification_type", "created_at"]),
        ]

    @property
    def recipient(self):
        return self.user

    def __str__(self):
        return self.title


class EmailNotification(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="email_notifications")
    subject = models.CharField(max_length=220)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def recipient(self):
        return self.user

    def __str__(self):
        return self.subject
