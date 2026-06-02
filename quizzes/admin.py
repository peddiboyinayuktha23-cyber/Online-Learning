from django.contrib import admin

from .models import Answer, Question, Quiz, QuizAttempt


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "timer_minutes", "passing_score", "is_active")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "course__title")
    autocomplete_fields = ("course",)
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "quiz", "question_type", "correct_answer", "points")
    search_fields = ("text", "quiz__title")
    autocomplete_fields = ("quiz",)


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("quiz", "student", "score", "passed", "started_at", "submitted_at")
    list_filter = ("passed", "started_at", "submitted_at")
    search_fields = ("quiz__title", "student__email")
    autocomplete_fields = ("quiz", "student")


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("attempt", "question", "selected_answer", "is_correct")
    autocomplete_fields = ("attempt", "question")
