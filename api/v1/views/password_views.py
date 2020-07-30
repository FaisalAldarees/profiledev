from rest_framework import permissions, generics, status
from rest_framework.response import Response

from django.contrib.auth import get_user_model

from users.tasks import send_change_password_task

from api.v1.serializers.password_serializer import ChangePasswordSerializer, SendChangePasswordLinkSerializer

import uuid


class SendChangePasswordLink(generics.UpdateAPIView):
    serializer_class = SendChangePasswordLinkSerializer
    authentication_classes = ()
    permission_classes = (permissions.AllowAny, )

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = get_user_model().objects.get(email=serializer.data.get("email"))
            send_change_password_task.delay(user.email)

            return Response({"success": "Eamil sent"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePassword(generics.UpdateAPIView):
    model = get_user_model()
    queryset = get_user_model().objects.all()
    serializer_class = ChangePasswordSerializer
    lookup_field = "password_token"
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user.password_token = uuid.uuid4()
            user.set_password(serializer.data.get("password"))
            user.save()

            return Response({"success": "Password changed"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
