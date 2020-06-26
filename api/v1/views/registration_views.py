from rest_framework import generics, permissions
from django.shortcuts import render

from api.v1.serializers.registration_serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)


def index(request):
    return render(request, 'index.html')
