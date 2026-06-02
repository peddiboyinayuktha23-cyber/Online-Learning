import uuid

from django.conf import settings
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from onlinelearning.core_models import AuditModel


class TimeStampedModel(AuditModel):
    class Meta:
        abstract = True


def unique_slug(model, value, instance=None):
    base_slug = slugify(value)[:220] or uuid.uuid4().hex[:8]
    slug = base_slug
    counter = 1
    query = model.objects.filter(slug=slug)
    if instance and instance.pk:
        query = query.exclude(pk=instance.pk)
    while query.exists():
        counter += 1
        slug = f"{base_slug}-{counter}"
        query = model.objects.filter(slug=slug)
        if instance and instance.pk:
            query = query.exclude(pk=instance.pk)
    return slug


class Course(TimeStampedModel):
    class Level(models.TextChoices):
        BEGINNER = "BEGINNER", "Beginner"
        INTERMEDIATE = "INTERMEDIATE", "Intermediate"
        ADVANCED = "ADVANCED", "Advanced"
        ALL_LEVELS = "ALL_LEVELS", "All levels"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=220, db_index=True)
    slug = models.SlugField(max_length=260, unique=True, blank=True)
    description = models.TextField()
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="courses_taught",
        limit_choices_to={"role": "INSTRUCTOR"},
    )
    category = models.ForeignKey("categories.Category", on_delete=models.PROTECT, related_name="courses")
    subcategory = models.ForeignKey(
        "categories.SubCategory",
        on_delete=models.PROTECT,
        related_name="courses",
        blank=True,
        null=True,
    )
    thumbnail = models.ImageField(upload_to="courses/thumbnails/%Y/%m/", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_free = models.BooleanField(default=False, db_index=True)
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.BEGINNER, db_index=True)
    language = models.CharField(max_length=60, default="English", db_index=True)
    is_published = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_published", "created_at"]),
            models.Index(fields=["category", "level"]),
            models.Index(fields=["instructor", "is_published"]),
            models.Index(fields=["price", "level"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Course, self.title, self)
        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        summary = getattr(self, "rating_summary", None)
        return summary.average_rating if summary else 0

    def __str__(self):
        return self.title


class CourseSection(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["course", "order"]
        constraints = [
            models.UniqueConstraint(fields=["course", "order"], name="unique_course_section_order"),
        ]

    def __str__(self):
        return f"{self.course}: {self.title}"


class Lesson(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    section = models.ForeignKey(
        CourseSection,
        on_delete=models.CASCADE,
        related_name="lessons",
        blank=True,
        null=True,
    )
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=220, blank=True)
    video_file = models.FileField(
        upload_to="courses/videos/%Y/%m/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["mp4", "mov", "m4v", "webm"])],
    )
    description = models.TextField(blank=True)
    duration = models.PositiveIntegerField(default=0, help_text="Duration in minutes.")
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_preview = models.BooleanField(default=False)

    class Meta:
        ordering = ["course", "order"]
        constraints = [
            models.UniqueConstraint(fields=["course", "order"], name="unique_lesson_order_per_course"),
            models.UniqueConstraint(fields=["course", "slug"], name="unique_lesson_slug_per_course"),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Lesson, self.title, self)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Resource(TimeStampedModel):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="resources")
    title = models.CharField(max_length=180)
    file = models.FileField(upload_to="courses/resources/%Y/%m/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["lesson", "order"]

    def __str__(self):
        return self.title


class WatchHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="watch_history")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="watch_events")
    watched_seconds = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    last_watched_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ["-last_watched_at"]
        constraints = [
            models.UniqueConstraint(fields=["student", "lesson"], name="unique_student_lesson_watch_history"),
        ]

    def __str__(self):
        return f"{self.student} watched {self.lesson}"


class Quiz(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="quizzes")
    title = models.CharField(max_length=180)
    passing_score = models.PositiveSmallIntegerField(default=70, validators=[MaxValueValidator(100)])

    class Meta:
        ordering = ["course", "title"]

    def __str__(self):
        return self.title


class Question(TimeStampedModel):
    class Answer(models.TextChoices):
        A = "A", "Option A"
        B = "B", "Option B"
        C = "C", "Option C"
        D = "D", "Option D"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=1, choices=Answer.choices)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["quiz", "order"]

    def __str__(self):
        return self.question_text[:80]


class Assignment(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assignments")
    title = models.CharField(max_length=180)
    description = models.TextField()
    due_date = models.DateTimeField(blank=True, null=True)
    attachment = models.FileField(upload_to="courses/assignments/%Y/%m/", blank=True, null=True)

    class Meta:
        ordering = ["course", "due_date", "title"]

    def __str__(self):
        return self.title


class Submission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions")
    uploaded_file = models.FileField(upload_to="submissions/%Y/%m/")
    notes = models.TextField(blank=True)
    grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-submitted_at"]
        constraints = [
            models.UniqueConstraint(fields=["assignment", "student"], name="unique_assignment_submission"),
        ]

    def __str__(self):
        return f"{self.student} - {self.assignment}"
