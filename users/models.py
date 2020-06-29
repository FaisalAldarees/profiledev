from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.postgres.fields import ArrayField, JSONField
from django.utils import timezone

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
    is_active = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = "email"


class UserEmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_email_verification')
    email_token = models.CharField(max_length=128)
    created_at = models.DateTimeField(default=timezone.now)


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profile",)
    avatar = models.ImageField(default="media/uploads/avatar/download.jpeg", upload_to=avatar_image_file_path,)
    job_experiences = ArrayField(JSONField(default=None, blank=True), default=None, blank=True, null=True,)
    education = ArrayField(JSONField(default=None, blank=True), default=None, blank=True, null=True,)
    certifications = ArrayField(JSONField(default=None, blank=True), default=None, blank=True, null=True,)
    about = models.TextField(default=None, null=True)
    social_info = ArrayField(JSONField(default=None, blank=True), default=None, blank=True, null=True,)
    skills = ArrayField(models.CharField(max_length=32), default=None, blank=True, null=True)
