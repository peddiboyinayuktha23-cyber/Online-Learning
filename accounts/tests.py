from django.contrib.auth import get_user_model
from django.test import TestCase


class CustomUserTests(TestCase):
    def test_email_login_user_creation(self):
        User = get_user_model()
        user = User.objects.create_user(email="student@example.com", username="student", password="Passw0rd!123")
        self.assertEqual(user.email, "student@example.com")
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertTrue(user.check_password("Passw0rd!123"))
