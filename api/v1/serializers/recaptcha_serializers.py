from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.utils.translation import ugettext_lazy as _

from api.v1.utils import verifiy_recaptcha


class ReCaptchaSerializer(serializers.Serializer):
    recaptcha = serializers.CharField(required=True, write_only=True)

    class Meta:
        fields = ["recaptcha"]

    def validate_recaptcha(self, value):
        if not verifiy_recaptcha(value):
            raise ValidationError(_("reCAPTCHA is incorrect"))
        return value
