from rest_framework import generics

from api.v1.serializers.registration_serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
