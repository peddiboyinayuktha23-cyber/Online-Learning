from django.contrib import admin

from .models import Enrollment, LessonProgress, Wishlist


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "progress", "completed", "enrolled_at", "completed_at")
    list_filter = ("completed", "enrolled_at", "completed_at")
    search_fields = ("student__email", "course__title")
    autocomplete_fields = ("student", "course")


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "lesson", "completed", "watched_seconds", "updated_at")
    list_filter = ("completed", "updated_at")
    autocomplete_fields = ("enrollment", "lesson")


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "created_at")
    search_fields = ("student__email", "course__title")
    autocomplete_fields = ("student", "course")
