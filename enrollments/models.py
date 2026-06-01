import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Enrollment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True, db_index=True)
    progress = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    completed = models.BooleanField(default=False, db_index=True)
    completed_at = models.DateTimeField(blank=True, null=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-enrolled_at"]
        constraints = [
            models.UniqueConstraint(fields=["student", "course"], name="unique_student_course_enrollment"),
        ]
        indexes = [
            models.Index(fields=["student", "completed"]),
            models.Index(fields=["course", "completed"]),
        ]

    @property
    def progress_percentage(self):
        return self.progress

    def mark_progress(self, percentage):
        self.progress = min(max(percentage, 0), 100)
        self.completed = self.progress >= 100
        if self.completed and not self.completed_at:
            self.completed_at = timezone.now()
        self.save(update_fields=["progress", "completed", "completed_at", "updated_at"])

    def __str__(self):
        return f"{self.student} enrolled in {self.course}"


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey("courses.Lesson", on_delete=models.CASCADE, related_name="student_progress")
    completed = models.BooleanField(default=False)
    watched_seconds = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["enrollment", "lesson"], name="unique_lesson_progress"),
        ]


class Wishlist(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist_items")
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="wishlisted_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["student", "course"], name="unique_student_course_wishlist"),
        ]

    def __str__(self):
        return f"{self.student} wants {self.course}"
