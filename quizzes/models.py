import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from onlinelearning.core_models import AuditModel


class Quiz(AuditModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="learning_quizzes")
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    timer_minutes = models.PositiveIntegerField(default=15)
    passing_score = models.PositiveSmallIntegerField(default=70, validators=[MinValueValidator(1), MaxValueValidator(100)])
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["course", "title"]

    def __str__(self):
        return self.title


class Question(AuditModel):
    class Type(models.TextChoices):
        MULTIPLE_CHOICE = "MULTIPLE_CHOICE", "Multiple choice"
        TRUE_FALSE = "TRUE_FALSE", "True/False"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_type = models.CharField(max_length=20, choices=Type.choices, default=Type.MULTIPLE_CHOICE)
    text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500, blank=True)
    option_d = models.CharField(max_length=500, blank=True)
    correct_answer = models.CharField(max_length=1, choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")])
    points = models.PositiveSmallIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["quiz", "order"]

    def __str__(self):
        return self.text[:80]


class QuizAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quiz_attempts")
    started_at = models.DateTimeField(default=timezone.now)
    submitted_at = models.DateTimeField(blank=True, null=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    passed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-started_at"]

    def calculate_score(self):
        answers = self.answers.select_related("question")
        earned = sum(answer.question.points for answer in answers if answer.is_correct)
        total = sum(question.points for question in self.quiz.questions.all()) or 1
        self.score = round((earned / total) * 100, 2)
        self.passed = self.score >= self.quiz.passing_score
        self.submitted_at = timezone.now()
        self.save(update_fields=["score", "passed", "submitted_at"])
        return self.score

    def __str__(self):
        return f"{self.student} - {self.quiz}"


class Answer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    selected_answer = models.CharField(max_length=1, choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["attempt", "question"], name="unique_quiz_attempt_answer"),
        ]

    @property
    def is_correct(self):
        return self.selected_answer == self.question.correct_answer
