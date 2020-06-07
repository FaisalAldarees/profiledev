from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from users import models

from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch


class ImageTests(TestCase):
    @patch("uuid.uuid4")
    def test_avatar_file_name_uuid(self, mock_uuid):
        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        file_path = models.avatar_image_file_path(None, "myimage.jpg")

        exp_path = f"uploads/avatar/{uuid}.jpg"
        self.assertEqual(file_path, exp_path)

