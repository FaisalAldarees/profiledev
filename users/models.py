from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone


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
