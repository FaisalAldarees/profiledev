from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("api:register")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class RegistrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()


    def test_create_valid_user_success(self):
        payload = {
            "email": "Bob@gmail.com",
            "first_name": "Bob",
            "last_name": "Alice",
            "password": "123456",
            "confirm_password": "123456",
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)


    def test_user_exist(self):
        payload = {
            "email": "Bob@gmail.com",
            "first_name": "Bob",
            "last_name": "Alice",
            "password": "123456",
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload, confirm_password = "123456")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_password_to_short(self):
        payload = {
            "email": "Bob@gmail.com",
            "first_name": "Bob",
            "last_name": "Alice",
            "password": "123",
            "confirm_password": "123",
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = (
            get_user_model().objects.filter(email=payload["email"]).exists()
        )
        self.assertFalse(user_exists)
