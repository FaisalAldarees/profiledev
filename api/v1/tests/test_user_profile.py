from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from users.models import UserProfile

from rest_framework.test import APIClient
from rest_framework import status


USER_INFO_URL = reverse("api:user_profile_update")


def create_user(**params):
    user = get_user_model().objects.create_user(
        **{
            "email": "Bob@gmail.com",
            "first_name": "Bob",
            "last_name": "Alice",
            "password": "123456",
        }
    )

    UserProfile.objects.create(user=user)
    return user


class UserInfoTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_valid_user_info(self):
        payload = {
            "job_experiences": [
                {
                    "company": "GeoTech",
                    "position": "web",
                    "location": "Riyadh",
                    "description": "Test description",
                    "from_date": "2020-1-1",
                    "to_date": "2020-2-2",
                },
                {
                    "company": "STC",
                    "position": "web",
                    "location": "Riyadh",
                    "description": "Test description",
                    "from_date": "2020-1-1",
                    "to_date": "2020-2-2",
                },
            ],
            "social_info": [
                {"name": "twitter", "username": "faisalaldarees"},
                {"name": "github", "username": "faisalaldarees"},
                {"name": "stackoverflow", "username": "faisalaldarees", },
                {"name": "linkedin", "username": "faisalaldarees"},
            ],
            "about": "This is a test about",
            "skills": ["Java", "Python", "HTML"],
        }
        res = self.client.put(USER_INFO_URL, payload, format="json")

        exp_res = {
            "job_experiences": [
                {
                    "company": "GeoTech",
                    "position": "web",
                    "location": "Riyadh",
                    "description": "Test description",
                    "from_date": "2020-01-01",
                    "to_date": "2020-02-02",
                },
                {
                    "company": "STC",
                    "position": "web",
                    "location": "Riyadh",
                    "description": "Test description",
                    "from_date": "2020-01-01",
                    "to_date": "2020-02-02",
                },
            ],
            "social_urls": [
                {"name": "twitter", "url": "www.twitter.com/faisalaldarees"},
                {"name": "github", "url": "www.github.com/faisalaldarees"},
                {
                    "name": "stackoverflow",
                    "url": "www.stackoverflow.com/faisalaldarees",
                },
                {"name": "linkedin", "url": "www.linkedin.com/faisalaldarees"},
            ],
            "about": "This is a test about",
            "skills": ["Java", "Python", "HTML"],
        }

        exp_res["user"] = self.user.id

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json(), exp_res)

    def test_social_site_not_supported(self):
        payload = {
            "job_experiences": [
                {
                    "company": "GeoTech",
                    "position": "web",
                    "location": "Riyadh",
                    "description": "Test description",
                    "from_date": "2020-1-1",
                    "to_date": "2020-2-2",
                },
                {
                    "company": "STC",
                    "position": "web",
                    "location": "Riyadh",
                    "description": "Test description",
                    "from_date": "2020-1-1",
                    "to_date": "2020-2-2",
                },
            ],
            "social_info": [
                {"name": "youtube", "username": "faisalaldarees"},
            ],
            "about": "This is a test about",
            "skills": ["Java", "Python", "HTML"],
        }

        res = self.client.put(USER_INFO_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Website not supported", res.json())

    def test_required_fields_not_given(self):
        payload = {
            "job_experiences": [
                {
                    "position": "web",
                    "location": "Riyadh",
                    "description": "Test description",
                    "from_date": "2020-1-1",
                    "to_date": "2020-2-2",
                },
            ],
            "social_info": [
                {"name": "youtube", "username": "faisalaldarees"},
            ],
            "about": "This is a test about",
            "skills": ["Java", "Python", "HTML"],
        }
        res = self.client.put(USER_INFO_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "company field is required",
            res.json()["job_experiences"][0]["non_field_errors"],
        )

    def test_from_date_greater_than_to_date(self):
        payload = {
            "job_experiences": [
                {
                    "position": "web",
                    "location": "Riyadh",
                    "description": "Test description",
                    "from_date": "2020-1-1",
                    "to_date": "2019-2-2",
                },
            ],
            "social_info": [
                {"name": "youtube", "username": "faisalaldarees"},
            ],
            "about": "This is a test about",
            "skills": ["Java", "Python", "HTML"],
        }
        res = self.client.put(USER_INFO_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "from_date in grater than to_date",
            res.json()["job_experiences"][0]["non_field_errors"],
        )
