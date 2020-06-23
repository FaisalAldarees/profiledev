from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APIClient
from rest_framework import status

from users.models import UserEmailVerification

from unittest.mock import patch


CREATE_USER_URL = reverse("api:registration")


class EmailVerificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            **{"email": "Bob@gmail.com", "first_name": "Bob", "last_name": "Alice", "password": "123456"}
        )
        self.client.force_authenticate(self.user)
        self.user_email_verification = UserEmailVerification.objects.create(user=self.user)

    @patch("api.v1.serializers.registration_serializers.send_verification_email")
    def test_email_sent_and_verified(self, sve):
        payload = {
            "email": "faisalaldarees@gmail.com",
            "first_name": "Bob",
            "last_name": "Alice",
            "password": "123456",
            "confirm_password": "123456",
        }

        res = self.client.post(CREATE_USER_URL, payload)
        user = get_user_model().objects.get(email=payload["email"])
        self.client.get("/v1/users/email/email_verification/{0}/".format(user.user_email_verification.email_token))
        user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(user.is_email_verified)
        self.assertEqual(sve.call_count, 1)

    @patch("api.v1.serializers.registration_serializers.send_verification_email")
    def test_link_expired(self, sve):
        payload = {
            "email": "faisalaldarees@gmail.com",
            "first_name": "Bob",
            "last_name": "Alice",
            "password": "123456",
            "confirm_password": "123456",
        }

        res1 = self.client.post(CREATE_USER_URL, payload)

        user = get_user_model().objects.get(email=payload["email"])
        user.user_email_verification.created_at = timezone.now() + timezone.timedelta(minutes=31)
        user.user_email_verification.save()

        res2 = self.client.get(
            "/v1/users/email/email_verification/{0}/".format(user.user_email_verification.email_token)
        )

        user.refresh_from_db()

        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user.is_email_verified)
        self.assertEqual(sve.call_count, 1)

    @patch("api.v1.serializers.registration_serializers.send_verification_email")
    def test_multiple_verifications(self, sve):
        payload = {
            "email": "faisalaldarees@gmail.com",
            "first_name": "Bob",
            "last_name": "Alice",
            "password": "123456",
            "confirm_password": "123456",
        }

        res1 = self.client.post(CREATE_USER_URL, payload)

        user = get_user_model().objects.get(email=payload["email"])

        self.client.get("/v1/users/email/email_verification/{0}/".format(user.user_email_verification.email_token))

        res2 = self.client.get(
            "/v1/users/email/email_verification/{0}/".format(user.user_email_verification.email_token)
        )

        user.refresh_from_db()

        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res2.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(user.is_email_verified)
        self.assertEqual(sve.call_count, 1)

    def test_wrong_verification_link(self):
        res = self.client.get(
            "/v1/users/email/email_verification/{0}/".format('wrong_path')
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
