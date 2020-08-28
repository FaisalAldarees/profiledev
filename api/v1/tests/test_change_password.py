from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APIClient
from rest_framework import status

from users.models import UserChangePassword

from unittest.mock import patch


SEND_CHANGE_PASSWORD_URL = reverse("api:send_change_password_link")
LOGIN_URL = reverse("api:login")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PasswordTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("api.v1.views.password_views.send_change_password_task.delay")
    def test_email_sent_and_password_changed(self, scp):
        payload = {
            "email": "Bob@gmail.com",
            "first_name": "Bob",
            "last_name": "Alice",
            "password": "123456",
        }

        user = create_user(**payload)
        with patch("api.v1.serializers.password_serializer.verifiy_recaptcha") as vr:
            vr.return_value = True
            res = self.client.patch(SEND_CHANGE_PASSWORD_URL, {"email": user.email, "recaptcha": "asdasd"})

        user.user_change_password.password_token = "test_password_token"
        user.user_change_password.save()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(scp.call_count, 1)
        self.assertTrue("sent", res.data)

        res = self.client.patch(
            "/v1/users/password/change/test_password_token/",
            {"password": "new_password", "confirm_password": "new_password"},
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue("changed", res.data)

        res = self.client.post(LOGIN_URL, {"email": user.email, "password": "new_password"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    @patch("api.v1.views.password_views.send_change_password_task.delay")
    def test_email_sent_and_password_does_not_matchup(self, scp):
        payload = {
            "email": "Bob@gmail.com",
            "first_name": "Bob",
            "last_name": "Alice",
            "password": "123456",
        }

        user = create_user(**payload)

        with patch("api.v1.serializers.password_serializer.verifiy_recaptcha") as vr:
            vr.return_value = True
            res = self.client.patch(SEND_CHANGE_PASSWORD_URL, {"email": user.email, "recaptcha": "asdasd"})

        user.user_change_password.password_token = "test_password_token"
        user.user_change_password.save()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(scp.call_count, 1)
        self.assertTrue("sent", res.data)

        res = self.client.patch(
            "/v1/users/password/change/test_password_token/",
            {"password": "new_password_0", "confirm_password": "new_password_1"},
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("changed", res.data)

        res = self.client.post(LOGIN_URL, {"email": user.email, "password": "new_password_0"})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("api.v1.views.password_views.send_change_password_task.delay")
    def test_email_sent_and_password_changed_twice(self, scp):
        payload = {
            "email": "Bob@gmail.com",
            "first_name": "Bob",
            "last_name": "Alice",
            "password": "123456",
        }

        user = create_user(**payload)

        with patch("api.v1.serializers.password_serializer.verifiy_recaptcha") as vr:
            vr.return_value = True
            res = self.client.patch(SEND_CHANGE_PASSWORD_URL, {"email": user.email, "recaptcha": "asdasd"})

        user.user_change_password.password_token = "test_password_token"
        user.user_change_password.save()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(scp.call_count, 1)
        self.assertTrue("sent", res.data)

        res = self.client.patch(
            "/v1/users/password/change/test_password_token/",
            {"password": "new_password", "confirm_password": "new_password"},
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue("changed", res.data)

        res = self.client.patch(
            "/v1/users/password/change/test_password_token/",
            {"password": "new_new_password", "confirm_password": "new_new_password"},
        )

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotIn("changed", res.data)

        res = self.client.post(LOGIN_URL, {"email": user.email, "password": "new_new_password"})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("api.v1.views.password_views.send_change_password_task.delay")
    def test_change_password_bad_token(self, scp):
        payload = {
            "email": "Bob@gmail.com",
            "first_name": "Bob",
            "last_name": "Alice",
            "password": "123456",
        }

        user = create_user(**payload)
        user_change_password = UserChangePassword.objects.create(user=user, password_token="test_password_token")
        user_change_password.created_at = timezone.now() - timezone.timedelta(seconds=31)
        user_change_password.save()

        res = self.client.patch(
            "/v1/users/password/change/wrong_token/",
            {"password": "new_password", "confirm_password": "new_password"},
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotIn("changed", res.data)

        res = self.client.post(LOGIN_URL, {"email": user.email, "password": "new_password"})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
