from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.conf import settings

from api.v1.utils import verifiy_recaptcha


class SendChangePasswordLinkSerializer(serializers.Serializer):
    email = serializers.EmailField(allow_blank=False)
    recaptcha = serializers.CharField(required=True, write_only=True)

    class Meta:
        fields = ["email", "recaptcha", ]

    def validate_email(self, value):
        user = get_user_model().objects.filter(email=value)
        if not user:
            raise ValidationError(_("Email does not exist"))
        return value

    def validate_recaptcha(self, value):
        if not settings.DEBUG and not verifiy_recaptcha(value):
            raise ValidationError(_("reCAPTCHA is incorrect"))
        return value


class ChangePasswordSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(allow_blank=False, write_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            "password",
            "confirm_password",
        )

    def validate(self, data):
        password = data.get("password")
        confirm_password = data.pop("confirm_password")

        if password != confirm_password:
            raise ValidationError(_("Passwords does not match up"))

        return data
