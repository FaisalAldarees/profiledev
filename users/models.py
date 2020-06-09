from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import ArrayField, JSONField
from django.utils.functional import cached_property

from rest_framework.serializers import ValidationError

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
        User,
        on_delete=models.CASCADE,
        related_name="info",
        default=None,
        null=True,
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
        urls = [{}, {}, {}, {}]
        count = 0
        for i in self.social_info:
            if i["name"].lower() not in [
                "twitter",
                "github",
                "stackoverflow",
                "linkedin",
            ]:
                raise ValidationError(_("Website not supported"))

            if i["name"] == "twitter":
                urls[count]["name"] = "twitter"
                urls[count]["url"] = f'www.twitter.com/{i["username"]}'

            if i["name"] == "github":
                urls[count]["name"] = "github"
                urls[count]["url"] = f'www.github.com/{i["username"]}'

            if i["name"] == "stackoverflow":
                urls[count]["name"] = "stackoverflow"
                urls[count]["url"] = f'www.stackoverflow.com/{i["username"]}'

            if i["name"] == "linkedin":
                urls[count]["name"] = "linkedin"
                urls[count]["url"] = f'www.linkedin.com/{i["username"]}'
            count += 1
        return urls
