from http import HTTPStatus

from django.test import TestCase

from .models import User


class UserFlowTests(TestCase):
    def test_register_and_login(self):
        register_response = self.client.post(
            "/users/register/",
            {
                "name": "Ivan",
                "surname": "Petrov",
                "email": "ivan@example.com",
                "password": "StrongPass123",
            },
        )
        self.assertEqual(register_response.status_code, HTTPStatus.FOUND)
        self.assertTrue(User.objects.filter(email="ivan@example.com").exists())

        login_response = self.client.post(
            "/users/login/",
            {"email": "ivan@example.com", "password": "StrongPass123"},
        )
        self.assertEqual(login_response.status_code, HTTPStatus.FOUND)
        self.assertEqual(login_response.url, "/projects/list")
