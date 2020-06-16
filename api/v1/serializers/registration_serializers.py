from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.core.mail import EmailMessage

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.db import transaction

from users.models import UserProfile, UserEmailVerification

import uuid


class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(allow_blank=False, write_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "first_name",
            "last_name",
            "password",
            "confirm_password",
        )
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def validate(self, data):
        password = data.get("password")
        confirm_password = data.pop("confirm_password")
        if password != confirm_password:
            raise ValidationError(_("Passwords does not match up"))
        return data

    def create(self, validated_data):
        with transaction.atomic():
            user = get_user_model().objects.create_user(**validated_data)
            user_email_verification = UserEmailVerification.objects.create(user=user, email_token=uuid.uuid4())
            UserProfile.objects.create(user=user)
            email = EmailMessage(
                "Verify your email",
                "CLick the link http://127.0.0.1:8000/v1/email/verify/{0}".format(user_email_verification.email_token),
                to=[user.email],
            )
            email.send()

        return user
