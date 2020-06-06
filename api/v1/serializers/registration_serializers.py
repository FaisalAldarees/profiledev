from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        label="Confirm Password", allow_blank=False, write_only=True
    )

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
            raise ValidationError("Passwords does not match up")
        return data

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)
