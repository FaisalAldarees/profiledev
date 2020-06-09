from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.postgres.fields import ArrayField, JSONField
from django.utils.functional import cached_property

import uuid
import os


def avatar_image_file_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"

    return os.path.join("uploads/avatar/", filename)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """create and saves a new user"""
        if not email:
            raise ValueError("user must have an email adress")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        raise NotImplementedError("Create super user is not supported")


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    objects = UserManager()

    USERNAME_FIELD = "email"


class UserProfile(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="profile",
    )
    avatar = models.ImageField(
        default="media/uploads/avatar/download.jpeg",
        upload_to=avatar_image_file_path,
    )
    job_experiences = ArrayField(
        JSONField(default=None, blank=True),
        default=None,
        blank=True,
        null=True,
    )
    about = models.TextField(default=None, null=True)
    social_info = ArrayField(
        JSONField(default=None, blank=True),
        default=None,
        blank=True,
        null=True,
    )
    skills = ArrayField(
        models.CharField(max_length=32), default=None, blank=True, null=True
    )

    @cached_property
    def social_urls(self):
        urls = []
        for i in self.social_info:
            if i["name"] == "twitter":
                urls.append(
                    {
                        "name": "twitter",
                        "url": "www.twitter.com/{0}".format(i["username"]),
                    }
                )
            if i["name"] == "github":
                urls.append(
                    {
                        "name": "github",
                        "url": "www.github.com/{0}".format(i["username"]),
                    }
                )
            if i["name"] == "stackoverflow":
                urls.append(
                    {
                        "name": "stackoverflow",
                        "url": "www.stackoverflow.com/{0}".format(
                            i["username"]
                        ),
                    }
                )
            if i["name"] == "linkedin":
                urls.append(
                    {
                        "name": "linkedin",
                        "url": "www.linkedin.com/{0}".format(i["username"]),
                    }
                )
        return urls
