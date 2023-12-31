from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from user_profile.models import UserProfile

from rest_framework.test import APIClient
from rest_framework import status


USER_INFO_URL = reverse("api:profile_update")


def create_user(**params):
    user = get_user_model().objects.create_user(
        **{"email": "Bob@gmail.com", "first_name": "Bob", "last_name": "Alice", "password": "123456"}
    )

    UserProfile.objects.create(user=user)
    user.is_email_verified = True
    return user


class UserInfoTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.profile = UserProfile.objects.get(user=self.user)
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
            "education": [
                {
                    "school": "ImamU",
                    "degree": "CS",
                    "location": "Riyadh",
                    "description": "Member of CyberHub student club",
                    "from_date": "2020-1-1",
                }
            ],
            "headline": "test headline",
            "location": "test location",
            "certifications": [
                {
                    "name": "Introduction to CyberSecurity",
                    "organization": "Cisco",
                    "url": "google.com",
                    "issue_date": "2020-1-1",
                }
            ],
            "social_info": [
                {"name": "twitter", "url": "www.twitter.com/faisalaldarees"},
                {"name": "github", "url": "www.github.com/faisalaldarees"},
                {"name": "stackoverflow", "url": "www.stackoverflow.com/faisalaldarees"},
                {"name": "linkedin", "url": "www.linkedin.com/faisalaldarees"},
            ],
            "about": "This is a test about",
            "skills": ["Java", "Python", "HTML"],
        }
        res = self.client.patch(USER_INFO_URL, payload, format="json")

        exp_res = {
            "first_name": "Bob",
            "last_name": "Alice",
            "job_experiences": [
                {
                    "company": "GeoTech",
                    "position": "web",
                    "location": "Riyadh",
                    "description": "Test description",
                    "from_date": "2020-01-01",
                    "to_date": "2020-02-02"
                },
                {
                    "company": "STC",
                    "position": "web",
                    "location": "Riyadh",
                    "description": "Test description",
                    "from_date": "2020-01-01",
                    "to_date": "2020-02-02"
                }
            ],
            "education": [
                {
                    "school": "ImamU",
                    "degree": "CS",
                    "location": "Riyadh",
                    "description": "Member of CyberHub student club",
                    "from_date": "2020-01-01",
                    "to_date": None
                }
            ],
            "headline": "test headline",
            "location": "test location",
            "certifications": [
                {
                    "name": "Introduction to CyberSecurity",
                    "organization": "Cisco",
                    "url": "google.com",
                    "issue_date": "2020-01-01",
                    "expiration_date": None
                }
            ],
            "social_info": [
                {"name": "twitter", "url": "www.twitter.com/faisalaldarees"},
                {"name": "github", "url": "www.github.com/faisalaldarees"},
                {"name": "stackoverflow", "url": "www.stackoverflow.com/faisalaldarees"},
                {"name": "linkedin", "url": "www.linkedin.com/faisalaldarees"}
            ],
            "about": "This is a test about",
            "skills": ["Java", "Python", "HTML"],
            "avatar": "http://testserver/media/media/uploads/avatar/default.jpeg",
            "user": self.user.id
        }
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json(), exp_res)

    def test_social_site_not_supported(self):
        payload = {"social_info": [{"name": "youtube", "url": "www.youtube.com/faisalaldarees"}]}

        res = self.client.patch(USER_INFO_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Website not supported", res.json()["social_info"][0]["name"])

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
            "education": [
                {
                }
            ],
            "certifications": [
                {
                }
            ]
        }
        res = self.client.patch(USER_INFO_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "company field is required", res.json()["job_experiences"][0]["non_field_errors"],
        )
        self.assertIn(
            "school field is required", res.json()["education"][0]["non_field_errors"],
        )
        self.assertIn(
            "name field is required", res.json()["certifications"][0]["non_field_errors"],
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
            "certifications": [
                {
                    "name": "Introduction to CyberSecurity",
                    "organization": "Cisco",
                    "issue_date": "2020-1-1",
                    "expiration_date": "2019-2-2"
                }
            ],
            "education": [
                {
                    "school": "ImamU",
                    "degree": "CS",
                    "from_date": "2020-1-1",
                    "to_date": "2019-2-2",
                }
            ],
        }
        res = self.client.patch(USER_INFO_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "from_date is grater than to_date", res.json()["job_experiences"][0]["non_field_errors"],
        )
        self.assertIn(
            "expiration_date is grater than to_date", res.json()["certifications"][0]["non_field_errors"],
        )
        self.assertIn(
            "from_date is grater than to_date", res.json()["education"][0]["non_field_errors"],
        )

    def test_from_date_is_invalid(self):
        payload = {
            "job_experiences": [
                {
                    "company": "GeoTech",
                    "position": "web",
                    "location": "Riyadh",
                    "description": "Test description",
                    "from_date": "4000-6-10",
                    "to_date": "5000-2-2",
                }
            ],
            "certifications": [
                {
                    "name": "Introduction to CyberSecurity",
                    "organization": "Cisco",
                    "issue_date": "4000-6-10",
                    "expiration_date": "5000-2-2"
                }
            ],
            "education": [
                {
                    "school": "ImamU",
                    "degree": "CS",
                    "from_date": "4000-6-10",
                    "to_date": "5000-2-2",
                }
            ],
        }
        res = self.client.patch(USER_INFO_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "the from_date is invalid", res.json()["job_experiences"][0]["from_date"],
        )
        self.assertIn(
            "the issue_date is invalid", res.json()["certifications"][0]["issue_date"],
        )
        self.assertIn(
            "the from_date is invalid", res.json()["education"][0]["from_date"],
        )

    def test_to_date_is_invalid(self):
        payload = {
            "job_experiences": [
                {
                    "company": "GeoTech",
                    "position": "web",
                    "location": "Riyadh",
                    "description": "Test description",
                    "from_date": "2010-6-10",
                    "to_date": "5000-2-2",
                }
            ],
            "certifications": [
                {
                    "name": "Introduction to CyberSecurity",
                    "organization": "Cisco",
                    "issue_date": "2010-6-10",
                    "expiration_date": "5000-2-2"
                }
            ],
            "education": [
                {
                    "school": "ImamU",
                    "degree": "CS",
                    "from_date": "2010-6-10",
                    "to_date": "5000-2-2",
                }
            ],
        }
        res = self.client.patch(USER_INFO_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "the to_date is invalid", res.json()["job_experiences"][0]["to_date"],
        )
        self.assertIn(
            "the expiration_date is invalid", res.json()["certifications"][0]["expiration_date"],
        )
        self.assertIn(
            "the to_date is invalid", res.json()["education"][0]["to_date"],
        )

    def test_put_patch(self):
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
                {"name": "twitter", "url": "www.twitter.com/faisalaldarees"},
                {"name": "github", "url": "www.github.com/faisalaldarees"},
                {"name": "stackoverflow", "url": "www.stackoverflow.com/faisalaldarees"},
                {"name": "linkedin", "url": "www.linkedin.com/faisalaldarees"},
            ],
            "about": "This is a test about",
            "skills": ["Java", "Python", "HTML"],
        }
        res1 = self.client.patch(USER_INFO_URL, payload, format="json")
        res2 = self.client.put(USER_INFO_URL, payload, format="json")
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
