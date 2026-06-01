from django.contrib.auth import get_user_model
from django.test import TestCase

from categories.models import Category

from .models import Course, Lesson


class CourseModelTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.instructor = User.objects.create_user(
            email="inst@example.com",
            username="inst",
            password="Passw0rd!123",
            role=User.Role.INSTRUCTOR,
        )
        self.category = Category.objects.create(name="Development")

    def test_course_slug_and_lesson_order(self):
        course = Course.objects.create(
            title="Python for Everyone",
            description="Learn Python",
            instructor=self.instructor,
            category=self.category,
            price=49,
            is_published=True,
        )
        Lesson.objects.create(course=course, title="Intro", order=1)
        self.assertEqual(course.slug, "python-for-everyone")
        self.assertEqual(course.lessons.count(), 1)
