from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APIClient
from rest_framework import status

from unittest.mock import patch


CREATE_USER_URL = reverse("api:registration")
RESEND_EMAIL_URL = reverse("api:resend_email_verification")


class EmailVerificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("api.v1.serializers.registration_serializers.send_verification_email_task.delay")
    def test_email_sent_and_verified(self, se):
        payload = {
            "email": "test@gmail.com",
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
        self.assertEqual(se.call_count, 1)

    @patch("api.v1.serializers.registration_serializers.send_verification_email_task.delay")
    def test_link_expired(self, se):
        payload = {
            "email": "test@gmail.com",
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
        self.assertEqual(se.call_count, 1)

    @patch("api.v1.serializers.registration_serializers.send_verification_email_task.delay")
    def test_multiple_verifications(self, se):
        payload = {
            "email": "test@gmail.com",
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
        self.assertEqual(se.call_count, 1)

    def test_wrong_verification_link(self):
        res = self.client.get("/v1/users/email/email_verification/{0}/".format("wrong_path"))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    @patch("api.v1.views.email_verification_views.send_verification_email_task.delay")
    def test_resend_email(self, se):
        payload = {
            "email": "test@gmail.com",
            "first_name": "Bob",
            "last_name": "Alice",
            "password": "123456",
            "confirm_password": "123456",
        }

        res1 = self.client.post(CREATE_USER_URL, payload)

        user = get_user_model().objects.get(email=payload["email"])
        user.user_email_verification.created_at = timezone.now() - timezone.timedelta(seconds=31)
        user.user_email_verification.save()

        self.client.force_authenticate(user)
        res2 = self.client.get(RESEND_EMAIL_URL)

        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(se.call_count, 2)

    @patch("api.v1.views.email_verification_views.send_verification_email_task.delay")
    def test_multiple_resend_email(self, se):
        payload = {
            "email": "test@gmail.com",
            "first_name": "Bob",
            "last_name": "Alice",
            "password": "123456",
            "confirm_password": "123456",
        }

        res1 = self.client.post(CREATE_USER_URL, payload)

        user = get_user_model().objects.get(email=payload["email"])
        user.user_email_verification.created_at = timezone.now() - timezone.timedelta(seconds=31)
        user.user_email_verification.save()

        self.client.force_authenticate(user)
        self.client.get(RESEND_EMAIL_URL)

        user.user_email_verification.created_at = timezone.now() - timezone.timedelta(seconds=29)
        user.user_email_verification.save()

        res2 = self.client.get(RESEND_EMAIL_URL)

        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(se.call_count, 2)
