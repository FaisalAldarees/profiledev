from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.db import transaction
from django.conf import settings

from api.v1.utils import verifiy_recaptcha

from users.models import UserEmailVerification
from users.tasks import send_verification_email_task

from user_profile.models import UserProfile

import uuid


class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(allow_blank=False, write_only=True)
    recaptcha = serializers.CharField(allow_blank=False, write_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "first_name",
            "last_name",
            "password",
            "confirm_password",
            "recaptcha",
        )
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def validate_recaptcha(self, value):
        if not settings.DEBUG and not verifiy_recaptcha(value):
            raise ValidationError(_("reCAPTCHA is incorrect"))

        return value

    def validate(self, data):
        data.pop("recaptcha")
        password = data.get("password")
        confirm_password = data.pop("confirm_password")
        if password != confirm_password:
            raise ValidationError(_("Passwords does not match up"))

        return data

    def create(self, validated_data):
        with transaction.atomic():
            user = get_user_model().objects.create_user(**validated_data)
            UserEmailVerification.objects.create(user=user, email_token=uuid.uuid4())
            UserProfile.objects.create(user=user)
            send_verification_email_task.delay(user.email)

        return user
