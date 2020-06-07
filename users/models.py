from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.postgres.fields import ArrayField, JSONField

import uuid
import os


def avatar_image_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/avatar/', filename)


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


class UserInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='info', default = None, null=True)
    avatar = models.ImageField(default = 'media/uploads/avatar/download.jpeg', upload_to=avatar_image_file_path)
    about = models.TextField(default = None, null=True)
    job_experience = ArrayField(JSONField(default = None, blank=True), default = None, blank=True,null=True)
    social_links = JSONField(null=True, blank=True)
    skills = ArrayField(models.CharField(max_length=255), default = None, blank=True,null=True)
