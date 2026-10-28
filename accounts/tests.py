from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class SignUpViewTests(TestCase):
    def test_signup_creates_aggregator_user(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "A-strong-password-123",
                "password2": "A-strong-password-123",
            },
        )

        self.assertRedirects(response, reverse("login"))
        user = get_user_model().objects.get(email="newuser@example.com")
        self.assertEqual(user.username, "newuser")
        self.assertTrue(user.check_password("A-strong-password-123"))
