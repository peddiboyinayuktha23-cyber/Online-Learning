from django import forms

from .models import Assignment, Course, Lesson, Quiz, Resource


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ("title", "description", "category", "thumbnail", "price", "level", "language", "is_published")


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ("course", "title", "video_file", "description", "duration", "order", "is_preview")


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ("lesson", "title", "file", "order")


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ("course", "title", "passing_score")


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ("course", "title", "description", "due_date", "attachment")
