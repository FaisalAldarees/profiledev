from rest_framework import generics, authentication, permissions
from api.v1.serializers.edit_profile_serializers import UserAvatarSerializer
from users.models import UserInfo


class AvatarRetrieveUpdate(generics.RetrieveUpdateAPIView):
    model = UserInfo
    serializer_class = UserAvatarSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def get_object(self):
        return UserInfo.objects.get(user=self.request.user)
