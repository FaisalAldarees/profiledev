from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from unittest.mock import patch


SEARCH_URL = reverse("api:search")
CREATE_USER_URL = reverse("api:registration")


class UserSearchTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("api.v1.serializers.registration_serializers.send_verification_email_task.delay")
    def test_valid_search(self, sve):
        payload_1 = {
            "email": "Bob@gmail.com",
            "first_name": "Bob",
            "last_name": "Alice",
            "password": "123456",
            "confirm_password": "123456",
            "recaptcha": "test",
        }

        payload_2 = {
            "email": "Alice@gmail.com",
            "first_name": "Alice",
            "last_name": "Bob",
            "password": "123456",
            "confirm_password": "123456",
            "recaptcha": "test",
        }

        with patch("api.v1.serializers.registration_serializers.verifiy_recaptcha") as vr:
            vr.return_value = True
            self.client.post(CREATE_USER_URL, payload_1)
            self.client.post(CREATE_USER_URL, payload_2)

        res = self.client.get(SEARCH_URL, {"query": "Bob Alice"})

        user_1 = get_user_model().objects.get(email=payload_1["email"])
        user_2 = get_user_model().objects.get(email=payload_2["email"])

        exp_res = [
            {
                "first_name": "Bob",
                "last_name": "Alice",
                "job_experiences": None,
                "education": None,
                "headline": None,
                "location": None,
                "certifications": None,
                "social_info": None,
                "about": None,
                "skills": None,
                "avatar": "http://testserver/media/media/uploads/avatar/default.jpeg",
                "user": user_1.id,
            },
            {
                "first_name": "Alice",
                "last_name": "Bob",
                "job_experiences": None,
                "education": None,
                "headline": None,
                "location": None,
                "certifications": None,
                "social_info": None,
                "about": None,
                "skills": None,
                "avatar": "http://testserver/media/media/uploads/avatar/default.jpeg",
                "user": user_2.id,
            },
        ]

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json(), exp_res)

    @patch("api.v1.serializers.registration_serializers.send_verification_email_task.delay")
    def test_search_query_not_found(self, sve):
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
            self.client.post(CREATE_USER_URL, payload)

        res = self.client.get(SEARCH_URL, {"query": "AmIThere???"})

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
