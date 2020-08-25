from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.serializers import ValidationError

from user_profile.models import UserProfile

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


class EducationSerializer(serializers.Serializer):

    school = serializers.CharField(max_length=255, required=False)
    degree = serializers.CharField(max_length=255, required=False)
    location = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(max_length=255, required=False)
    from_date = serializers.DateField(required=False, allow_null=True)
    to_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        fields = [
            "school",
            "degree",
            "location",
            "description",
            "from_date",
            "to_date",
        ]

    def validate(self, data):
        if "from_date" and "to_date" in data:
            if data["to_date"] < data["from_date"]:
                raise ValidationError(_("from_date is grater than to_date"))
        if "school" not in data:
            raise ValidationError(_("school field is required"))
        if "degree" not in data:
            raise ValidationError(_("degree field is required"))

        return data

    def validate_from_date(self, value):
        if value > date.today():
            raise ValidationError(_("the from_date is invalid"))

        return value.strftime("%Y-%m-%d")

    def validate_to_date(self, value):
        if value > date.today():
            raise ValidationError(_("the to_date is invalid"))
        return value.strftime("%Y-%m-%d")


class CertificationSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=255)
    organization = serializers.CharField(max_length=255)
    url = serializers.CharField(max_length=255, required=False)
    issue_date = serializers.DateField(required=False, allow_null=True)
    expiration_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        fields = [
            "name",
            "organization",
            "url",
            "issue_date",
            "expiration_date",
        ]

    def validate(self, data):
        if "issue_date" and "expiration_date" in data:
            if data["expiration_date"] < data["issue_date"]:
                raise ValidationError(_("expiration_date is grater than to_date"))
        if "name" not in data:
            raise ValidationError(_("name field is required"))
        if "organization" not in data:
            raise ValidationError(_("organization field is required"))

        return data

    def validate_issue_date(self, value):
        if value > date.today():
            raise ValidationError(_("the issue_date is invalid"))

        return value.strftime("%Y-%m-%d")

    def validate_expiration_date(self, value):
        if value > date.today():
            raise ValidationError(_("the expiration_date is invalid"))
        return value.strftime("%Y-%m-%d")


class SocialInfoSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    url = serializers.CharField(max_length=255)

    class Meta:
        fields = ["name", "url"]

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
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    job_experiences = JobExperienceSerializer(many=True, required=False, allow_null=True)
    education = EducationSerializer(many=True, required=False, allow_null=True)
    certifications = CertificationSerializer(many=True, required=False, allow_null=True)
    social_info = SocialInfoSerializer(many=True, required=False, allow_null=True)
    skills = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)

    class Meta:
        model = UserProfile
        fields = [
            "first_name",
            "last_name",
            "job_experiences",
            "education",
            "certifications",
            "social_info",
            "about",
            "headline",
            "location",
            "skills",
            "avatar",
            "user",
        ]
        read_only_fields = ("user", "avatar")
