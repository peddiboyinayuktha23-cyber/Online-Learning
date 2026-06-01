from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


class AuthenticationApiTests(APITestCase):
    def test_register_and_login(self):
        payload = {
            "username": "learner",
            "email": "learner@example.com",
            "password": "Passw0rd!123",
            "confirm_password": "Passw0rd!123",
            "first_name": "Learner",
            "last_name": "One",
            "role": "STUDENT",
        }
        response = self.client.post("/api/v1/auth/register/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        login = self.client.post("/api/v1/auth/login/", {"email": payload["email"], "password": payload["password"]})
        self.assertEqual(login.status_code, 200)
        self.assertIn("access", login.data)

    def test_me_requires_auth(self):
        User = get_user_model()
        user = User.objects.create_user(email="student2@example.com", username="student2", password="Passw0rd!123")
        self.client.force_authenticate(user=user)
        response = self.client.get("/api/v1/users/me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], user.email)
