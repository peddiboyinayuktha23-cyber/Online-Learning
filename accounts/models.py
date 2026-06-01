from django.contrib.auth.models import AbstractUser
from django.db import models

from .manager import CustomUserManager


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "STUDENT", "Student"
        INSTRUCTOR = "INSTRUCTOR", "Instructor"
        ADMIN = "ADMIN", "Admin"

    email = models.EmailField(unique=True, db_index=True)
    profile_picture = models.ImageField(upload_to="profiles/%Y/%m/", blank=True, null=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True, db_index=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT, db_index=True)
    email_verified = models.BooleanField(default=False, db_index=True)
    email_verification_token = models.CharField(max_length=128, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    class Meta:
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["role", "is_active"]),
            models.Index(fields=["email", "role"]),
        ]

    def save(self, *args, **kwargs):
        if self.is_superuser or self.is_staff:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return self.get_full_name() or self.username or self.email

    @full_name.setter
    def full_name(self, value):
        parts = (value or "").strip().split(" ", 1)
        self.first_name = parts[0] if parts else ""
        self.last_name = parts[1] if len(parts) > 1 else ""

    @property
    def profile_image(self):
        return self.profile_picture

    @property
    def phone_number(self):
        return self.phone

    def __str__(self):
        return self.full_name


class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="student_profile")
    headline = models.CharField(max_length=180, blank=True)
    learning_goals = models.TextField(blank=True)
    interests = models.ManyToManyField("categories.Category", blank=True, related_name="interested_students")
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Student profile: {self.user}"


class InstructorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="instructor_profile")
    expertise = models.CharField(max_length=180, blank=True, db_index=True)
    experience_years = models.PositiveSmallIntegerField(default=0)
    linkedin_url = models.URLField(blank=True)
    website = models.URLField(blank=True)
    total_students = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    is_featured = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Instructor profile: {self.user}"
