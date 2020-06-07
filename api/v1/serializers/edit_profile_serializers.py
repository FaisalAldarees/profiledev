from django.contrib.auth import get_user_model
from users.models import UserInfo
from rest_framework.serializers import ModelSerializer


class UserAvatarSerializer(ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ["avatar", "user"]
        read_only_fields = ("user",)
