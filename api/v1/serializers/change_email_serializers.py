from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.conf import settings

from api.v1.utils import verifiy_recaptcha


class ChangeEamilSerializer(serializers.ModelSerializer):
    recaptcha = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "recaptcha",
        )

    def validate_email(self, value):
        user = get_user_model().objects.filter(email=value)
        if user:
            raise ValidationError(_("Email already exists"))
        return value

    def validate_recaptcha(self, value):
        if not settings.DEBUG and not verifiy_recaptcha(value):
            raise ValidationError(_("reCAPTCHA is incorrect"))
        return value
