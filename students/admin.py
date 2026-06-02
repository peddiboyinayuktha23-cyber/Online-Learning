from django.contrib import admin

from .models import StudentNote


@admin.register(StudentNote)
class StudentNoteAdmin(admin.ModelAdmin):
    list_display = ("student", "title", "created_at")
    search_fields = ("student__email", "title", "body")
    autocomplete_fields = ("student",)
