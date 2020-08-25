from rest_framework import permissions, generics, status
from rest_framework.response import Response

from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model

from users.tasks import send_verification_email_task
from users.models import UserEmailVerification

from api.v1.serializers.recaptcha_serializers import ReCaptchaSerializer
from api.v1.serializers.change_email_serializers import ChangeEamilSerializer

from datetime import timedelta

import uuid


class VerifyEmail(generics.RetrieveAPIView):
    model = UserEmailVerification
    queryset = UserEmailVerification.objects.all()
    lookup_field = "email_token"
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def retrieve(self, request, *args, **kwargs):
        user_email_verification = super().get_object()
        user = user_email_verification.user
        wait_time = timezone.now() + timedelta(minutes=30)

        if user_email_verification.created_at <= wait_time:
            with transaction.atomic():
                user.is_email_verified = True
                user_email_verification.email_token = uuid.uuid4()
                user_email_verification.created_at = timezone.now()
                user_email_verification.save()
                user.save()

        if not user.is_email_verified:
            return Response({"verified": False}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"verified": True}, status=status.HTTP_200_OK)


class ResendEmail(generics.UpdateAPIView):
    model = UserEmailVerification
    queryset = UserEmailVerification.objects.all()
    serializer_class = ReCaptchaSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return UserEmailVerification.objects.get(user=self.request.user)

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():

            wait_time = timezone.now() - timedelta(seconds=30)
            user_email_verification = self.get_object()

            if user_email_verification.created_at < wait_time:
                send_verification_email_task.delay(user_email_verification.user.email)
                return Response({"resent": True}, status=status.HTTP_200_OK)

            else:
                return Response({"resent": False}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeEmail(generics.UpdateAPIView):
    model = get_user_model()
    queryset = get_user_model().objects.all()
    serializer_class = ChangeEamilSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return get_user_model().objects.get(id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = self.get_object()
            user.email = serializer.data.get("email")
            user.is_email_verified = False
            user.save()
            send_verification_email_task.delay(user.email)
            return Response({"succsess": "Check your email inbox for verification"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
