from django.contrib import admin

from .models import Assignment, Course, CourseSection, Lesson, Question, Quiz, Resource, Submission, WatchHistory


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ("title", "order", "duration", "is_preview")


class CourseSectionInline(admin.TabularInline):
    model = CourseSection
    extra = 0
    fields = ("title", "order")


class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 0
    fields = ("title", "file", "order")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "instructor", "category", "price", "level", "language", "is_published", "created_at")
    list_filter = ("is_published", "level", "language", "category", "created_at")
    search_fields = ("title", "description", "instructor__email", "category__name")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("instructor", "category")
    inlines = [CourseSectionInline, LessonInline]


@admin.register(CourseSection)
class CourseSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    search_fields = ("title", "course__title")
    autocomplete_fields = ("course",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order", "duration", "is_preview")
    list_filter = ("is_preview", "created_at")
    search_fields = ("title", "description", "course__title")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("course", "section")
    inlines = [ResourceInline]


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson", "order")
    search_fields = ("title", "lesson__title")
    autocomplete_fields = ("lesson",)


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ("question_text", "option_a", "option_b", "option_c", "option_d", "correct_answer", "order")


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "passing_score")
    search_fields = ("title", "course__title")
    autocomplete_fields = ("course",)
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_text", "quiz", "correct_answer", "order")
    search_fields = ("question_text", "quiz__title")
    autocomplete_fields = ("quiz",)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "due_date")
    search_fields = ("title", "course__title")
    autocomplete_fields = ("course",)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("assignment", "student", "grade", "submitted_at")
    search_fields = ("assignment__title", "student__email")
    autocomplete_fields = ("assignment", "student")


@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    list_display = ("student", "lesson", "watched_seconds", "completed", "last_watched_at")
    list_filter = ("completed", "last_watched_at")
    search_fields = ("student__email", "lesson__title")
    autocomplete_fields = ("student", "lesson")
