from rest_framework import generics, permissions
from api.v1.serializers.edit_profile_serializers import (
    UserAvatarSerializer,
    UserProfileSerializer,
)
from users.models import UserProfile


class AvatarUpdate(generics.UpdateAPIView):
    model = UserProfile
    serializer_class = UserAvatarSerializer
    lookup_field = "user_id"

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)


class AvatarRetrieve(generics.RetrieveAPIView):
    model = UserProfile
    serializer_class = UserAvatarSerializer
    lookup_field = "user_id"
    queryset = UserProfile.objects.all()
    authentication_classes = ()
    permission_classes = (permissions.AllowAny, )


class UserProfileUpdate(generics.UpdateAPIView):
    model = UserProfile
    serializer_class = UserProfileSerializer

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)


class UserProfileRetrive(generics.RetrieveAPIView):
    model = UserProfile
    serializer_class = UserProfileSerializer
    lookup_field = 'user_id'
    queryset = UserProfile.objects.all()
    authentication_classes = ()
    permission_classes = (permissions.AllowAny, )
