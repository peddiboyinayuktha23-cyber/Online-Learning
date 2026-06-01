from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], db_index=True)
    comment = models.TextField()
    is_approved = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "review"
        verbose_name_plural = "reviews"
        constraints = [
            models.UniqueConstraint(fields=["student", "course"], name="unique_student_course_review"),
        ]
        indexes = [
            models.Index(fields=["course", "rating"]),
            models.Index(fields=["is_approved", "created_at"]),
        ]

    def __str__(self):
        return f"{self.course} - {self.rating} stars"


class Rating(models.Model):
    course = models.OneToOneField("courses.Course", on_delete=models.CASCADE, related_name="rating_summary")
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-average_rating"]
        verbose_name = "rating summary"
        verbose_name_plural = "rating summaries"

    def __str__(self):
        return f"{self.course} rating: {self.average_rating}"


class Reply(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="replies")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="review_replies")
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "review reply"
        verbose_name_plural = "review replies"

    def __str__(self):
        return f"Reply by {self.user}"
