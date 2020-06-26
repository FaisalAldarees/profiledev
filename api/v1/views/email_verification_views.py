from rest_framework import permissions, generics, status
from rest_framework.response import Response

from django.utils import timezone
from django.db import transaction

from users.tasks import send_verification_email_task


from users.models import UserEmailVerification

from datetime import timedelta


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
                user_email_verification.delete()
                user.save()

        if not user.is_email_verified:
            return Response({"verified": False}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"verified": True}, status=status.HTTP_200_OK)


class ResendEmail(generics.RetrieveAPIView):
    model = UserEmailVerification
    queryset = UserEmailVerification.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return UserEmailVerification.objects.get(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        wait_time = timezone.now() - timedelta(seconds=30)
        user_email_verification = self.get_object()
        if user_email_verification.created_at < wait_time:
            send_verification_email_task.delay(user_email_verification.user.email)
            return Response({"resent": True}, status=status.HTTP_200_OK)
        else:
            return Response({"resent": False}, status=status.HTTP_400_BAD_REQUEST)
