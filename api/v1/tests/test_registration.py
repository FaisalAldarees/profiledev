from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from unittest.mock import patch


CREATE_USER_URL = reverse("api:registration")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class RegistrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("api.v1.serializers.registration_serializers.send_verification_email_task.delay")
    def test_create_valid_user_success(self, sve):
        payload = {
            "email": "Bob@gmail.com",
            "first_name": "Bob",
            "last_name": "Alice",
            "password": "123456",
            "confirm_password": "123456",
            "recaptcha": "test",
        }

        with patch("api.v1.serializers.registration_serializers.verifiy_recaptcha") as vr:
            vr.return_value = True
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

        with patch("api.v1.serializers.registration_serializers.verifiy_recaptcha") as vr:
            vr.return_value = True
            res = self.client.post(CREATE_USER_URL, payload, confirm_password="123456", recaptcha="test")

        self.assertEqual("user with this email already exists.", str(res.data["email"][0]))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(res.data["email"][0], "user with this email already exists.")

    def test_password_to_short(self, ):
        payload = {
            "email": "Bob@gmail.com",
            "first_name": "Bob",
            "last_name": "Alice",
            "password": "123",
            "confirm_password": "123",
            "recaptcha": "test",
        }

        with patch("api.v1.serializers.registration_serializers.verifiy_recaptcha") as vr:
            vr.return_value = True
            res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            "Ensure this field has at least 5 characters.", str(res.data["password"][0]),
        )

        user_exists = get_user_model().objects.filter(email=payload["email"]).exists()

        self.assertFalse(user_exists)

    def test_password_does_not_match(self, ):
        payload = {
            "email": "Bob@gmail.com",
            "first_name": "Bob",
            "last_name": "Alice",
            "password": "123456",
            "confirm_password": "1234567",
            "recaptcha": "test",
        }

        with patch("api.v1.serializers.registration_serializers.verifiy_recaptcha") as vr:
            vr.return_value = True
            res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual("Passwords does not match up", str(res.data["non_field_errors"][0]))

    def test_user_email_not_provided(self, ):
        payload = {
            "email": "",
            "first_name": "Bob",
            "last_name": "Alice",
            "password": "1234567",
            "confirm_password": "1234567",
            "recaptcha": "test",
        }

        with patch("api.v1.serializers.registration_serializers.verifiy_recaptcha") as vr:
            vr.return_value = True
            res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual("This field may not be blank.", str(res.data["email"][0]))

    def test_user_first_name_not_provided(self, ):
        payload = {
            "email": "Bob@gmail.com",
            "first_name": "",
            "last_name": "Alice",
            "password": "123456",
            "confirm_password": "1234567",
            "recaptcha": "test",
        }

        with patch("api.v1.serializers.registration_serializers.verifiy_recaptcha") as vr:
            vr.return_value = True
            res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual("This field may not be blank.", str(res.data["first_name"][0]))

    def test_user_last_name_not_provided(self, ):
        payload = {
            "email": "Bob@gmail.com",
            "first_name": "Bob",
            "last_name": "",
            "password": "1234567",
            "confirm_password": "1234567",
            "recaptcha": "test",
        }

        with patch("api.v1.serializers.registration_serializers.verifiy_recaptcha") as vr:
            vr.return_value = True
            res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual("This field may not be blank.", str(res.data["last_name"][0]))

    def test_user_password_not_provided(self, ):
        payload = {
            "email": "bob@gmail.com",
            "first_name": "Bob",
            "last_name": "Alice",
            "password": "",
            "confirm_password": "1234567",
            "recaptcha": "test",
        }

        with patch("api.v1.serializers.registration_serializers.verifiy_recaptcha") as vr:
            vr.return_value = True
            res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual("This field may not be blank.", str(res.data["password"][0]))

    def test_user_confirm_password_not_provided(self, ):
        payload = {
            "email": "bob@gmail.com",
            "first_name": "Bob",
            "last_name": "Alice",
            "password": "123456",
            "confirm_password": "",
            "recaptcha": "test",
        }

        with patch("api.v1.serializers.registration_serializers.verifiy_recaptcha") as vr:
            vr.return_value = True
            res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            "This field may not be blank.", str(res.data["confirm_password"][0]),
        )
