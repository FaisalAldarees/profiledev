from rest_framework import permissions, generics, status
from rest_framework.response import Response

from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

from users.tasks import send_change_password_task
from users.models import UserChangePassword

from api.v1.serializers.password_serializer import (
    SendChangePasswordLinkSerializer,
    ChangePasswordSerializer,
    ChangePasswordWhenLoggedInSerializer,
)

from datetime import timedelta

import uuid


class ChangePassword(generics.UpdateAPIView):
    model = UserChangePassword
    queryset = UserChangePassword.objects.all()
    serializer_class = ChangePasswordSerializer
    lookup_field = "password_token"
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user_change_password = super().get_object()
            user = user_change_password.user
            wait_time = timezone.now() + timedelta(minutes=30)

            if user_change_password.created_at <= wait_time:
                with transaction.atomic():
                    user_change_password.delete()
                    user.set_password(serializer.data.get("password"))
                    user.save()
                return Response({"changed": True}, status=status.HTTP_200_OK)
            else:
                return Response({"changed": False}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendChangePasswordLink(generics.UpdateAPIView):
    serializer_class = SendChangePasswordLinkSerializer
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():

            wait_time = timezone.now() - timedelta(seconds=30)
            current_time = timezone.now()
            user = get_user_model().objects.get(email=serializer.data.get("email"))
            user_change_password = UserChangePassword.objects.filter(user=user)

            if not user_change_password:
                user_change_password = UserChangePassword.objects.create(
                    user=user, password_token=uuid.uuid4(), created_at=current_time
                )

            if user_change_password.created_at < wait_time or user_change_password.created_at == current_time:
                send_change_password_task.delay(user.email)
                return Response({"sent": True}, status=status.HTTP_200_OK)

            else:
                return Response({"sent": False}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordWhenLoggedIn(generics.UpdateAPIView):
    model = get_user_model()
    queryset = get_user_model().objects.all()
    serializer_class = ChangePasswordWhenLoggedInSerializer
    permission_classes = (permissions.AllowAny,)

    def get_object(self):
        return get_user_model().objects.get(id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = self.get_object()
            with transaction.atomic():
                if check_password(serializer.validated_data.get("current_password"), user.password):
                    user.set_password(serializer.validated_data.get("password"))
                    user.save()
                    return Response({"changed": True}, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {"current_password": "current password is incorrect"}, status=status.HTTP_400_BAD_REQUEST
                    )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
