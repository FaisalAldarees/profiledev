from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from user_profile import models
from user_profile.models import UserProfile

import tempfile
import os

from PIL import Image

from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch

UPDATE_AVATAR_URL = reverse("api:avatar_update")


class AvatarTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            **{"email": "Bob@gmail.com", "first_name": "Bob", "last_name": "Alice", "password": "123456"}
        )
        self.user.is_email_verified = True
        self.client.force_authenticate(self.user)
        self.user_info = UserProfile.objects.create(user=self.user)

    def tearDown(self):
        self.user_info.avatar.delete()

    @patch("uuid.uuid4")
    def test_avatar_file_name_uuid(self, mock_uuid):
        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        file_path = models.avatar_image_file_path(None, "myimage.jpg")

        exp_path = f"uploads/avatar/{uuid}.jpg"
        self.assertEqual(file_path, exp_path)

    def test_update_avatar(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.patch(UPDATE_AVATAR_URL, {"avatar": ntf}, format="multipart")
        self.user_info.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("avatar", res.data)
        self.assertTrue(os.path.exists(self.user_info.avatar.path))

    def test_upload_image_bad_request(self):
        res = self.client.patch(UPDATE_AVATAR_URL, {"avatar": "notimage"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
