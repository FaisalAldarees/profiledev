from users.models import UserProfile

from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.serializers import ValidationError

from datetime import date


class UserAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["avatar", "user"]
        read_only_fields = ("user",)


class JobExperienceSerializer(serializers.Serializer):

    company = serializers.CharField(max_length=255, required=False)
    position = serializers.CharField(max_length=255, required=False)
    location = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(max_length=255, required=False)
    from_date = serializers.DateField(required=False, allow_null=True)
    to_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        fields = [
            "company",
            "position",
            "location",
            "description",
            "from_date",
            "to_date",
        ]

    def validate(self, data):
        if "from_date" and "to_date" in data:
            if data["to_date"] < data["from_date"]:
                raise ValidationError(_("from_date is grater than to_date"))
        if "company" not in data:
            raise ValidationError(_("company field is required"))
        return data

    def validate_from_date(self, value):
        if value > date.today():
            raise ValidationError(_("the from_date is invalid"))

        return value.strftime("%Y-%m-%d")

    def validate_to_date(self, value):
        if value > date.today():
            raise ValidationError(_("the to_date is invalid"))
        return value.strftime("%Y-%m-%d")


class SocialInfoSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255)

    class Meta:
        fields = ["name", "username"]

    def validate_name(self, value):
        if value.lower() not in [
            "twitter",
            "github",
            "stackoverflow",
            "linkedin",
        ]:
            raise ValidationError(_("Website not supported"))
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    job_experiences = JobExperienceSerializer(
        many=True, required=False, allow_null=True
    )
    social_info = SocialInfoSerializer(
        many=True, required=False, allow_null=True, write_only=True
    )
    skills = serializers.ListField(
        child=serializers.CharField(), required=False, allow_null=True
    )

    class Meta:
        model = UserProfile
        fields = [
            "job_experiences",
            "social_info",
            "social_urls",
            "about",
            "skills",
            "user",
        ]
        read_only_fields = ("user", "social_urls")
