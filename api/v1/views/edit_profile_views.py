from rest_framework import generics, permissions, status
from rest_framework.response import Response

from api.v1.serializers.edit_profile_serializers import (
    UserAvatarSerializer,
    UserProfileSerializer,
)
from users.models import UserProfile


class AvatarUpdate(generics.UpdateAPIView):
    model = UserProfile
    serializer_class = UserAvatarSerializer

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)


class AvatarRetrieve(generics.RetrieveAPIView):
    model = UserProfile
    lookup_field = "user_id"
    serializer_class = UserAvatarSerializer
    queryset = UserProfile.objects.all()
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def retrieve(self, request, *args, **kwargs):
        if not self.get_object().user.is_email_verified:
            err = {"error": "user not verified"}
            return Response(err, status=status.HTTP_404_NOT_FOUND)
        else:
            return super().retrieve()


class UserProfileUpdate(generics.UpdateAPIView):
    model = UserProfile
    serializer_class = UserProfileSerializer

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)


class UserProfileRetrive(generics.RetrieveAPIView):
    model = UserProfile
    serializer_class = UserProfileSerializer
    lookup_field = "user_id"
    queryset = UserProfile.objects.all()
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def retrieve(self, request, *args, **kwargs):
        if not self.get_object().user.is_email_verified:
            err = {"error": "user not verified"}
            return Response(err, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
