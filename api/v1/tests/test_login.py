from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


LOGIN_URL = reverse("api:login")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class LoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_token_for_user(self):
        payload = {"email": "test@gmail.com", "password": "123456"}
        create_user(**payload)
        res = self.client.post(LOGIN_URL, payload)
        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        create_user(email="test@gmail.com", password="123456")
        payload = {"email": "test@gmail.com", "password": "inv@l1d_p@$$w0rd"}
        res = self.client.post(LOGIN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def create_token_no_user(self):
        payload = {"email": "test@gmail.com", "password": "123456"}
        res = self.client.post(LOGIN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_fields(self):
        res = self.client.post(LOGIN_URL, {"email": "test@gmail.com"})
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
