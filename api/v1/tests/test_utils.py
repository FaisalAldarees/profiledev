from django.test import TestCase
from django.contrib.auth import get_user_model

from users.models import UserEmailVerification
from user_profile.models import UserProfile
from api.v1.utils import send_verification_email, delete_unverified_users

from rest_framework.test import APIClient

from unittest.mock import patch


def create_user(**params):
    user = get_user_model().objects.create_user(
        **{"email": "Bob@gmail.com", "first_name": "Bob", "last_name": "Alice", "password": "123456"}
    )

    UserProfile.objects.create(user=user)
    UserEmailVerification.objects.create(user=user)
    return user


class UtilsTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_delete_unverified_users(self):
        delete_unverified_users()
        self.assertNotIn(self.user, get_user_model().objects.all())

    @patch("api.v1.utils.EmailMessage")
    def test_sending_verification_email(self, se):
        send_verification_email(self.user.email)
        self.assertEqual(se.call_count, 1)
