from rest_framework import permissions, generics, status
from rest_framework.response import Response

from django.utils import timezone

from api.v1.serializers.registration_serializers import UserSerializer
from api.v1.utils import send_verification_email

from users.models import UserEmailVerification, User

from datetime import timedelta


class VerifyEmail(generics.RetrieveAPIView):
    model = UserEmailVerification
    queryset = UserEmailVerification.objects.all()
    serializer_class = UserSerializer
    lookup_field = "email_token"
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def get_object(self):
        user_email_verification = super().get_object()
        user = user_email_verification.user
        wait_time = timezone.now() + timedelta(minutes=30)

        if user_email_verification.created_at <= wait_time:
            user.is_email_verified = True
            user.save()

        return user

    def retrieve(self, request, *args, **kwargs):
        if not self.get_object().is_email_verified:
            err = {"error": "link has expired"}
            return Response(err, status=status.HTTP_404_NOT_FOUND)
        else:
            return super().retrieve(self.request)


class ResentEmail(generics.RetrieveAPIView):
    model = User
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        wait_time = timezone.now() - timedelta(seconds=30)
        user_email_verification = UserEmailVerification.objects.get(user=self.request.user)
        user = self.request.user
        if user_email_verification.created_at < wait_time:
            send_verification_email(user_email_verification)

        return user
