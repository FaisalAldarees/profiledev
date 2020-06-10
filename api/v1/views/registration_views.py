from rest_framework import generics, permissions

from api.v1.serializers.registration_serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)
