from rest_framework import permissions, generics, status
from rest_framework.response import Response

from django.core.mail import EmailMessage
from django.utils import timezone

from api.v1.serializers.registration_serializers import UserSerializer

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
        self.user_email_verification = UserEmailVerification.objects.get(email_token=self.kwargs["email_token"])
        user = UserEmailVerification.objects.get(email_token=self.kwargs["email_token"]).user
        wait_time = timezone.now() + timedelta(minutes=30)

        if self.user_email_verification.created_at <= wait_time:
            user.is_email_verified = True
            user.save()

        return user

    def retrieve(self, request, *args, **kwargs):
        if not self.get_object().is_email_verified:
            err = {"error": "link has expired"}
            return Response(err, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            self.user_email_verification.delete()
            return Response(serializer.data)


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
            email = EmailMessage(
                "Verify your email",
                "CLick the link http://127.0.0.1:8000/v1/email/verify/{0}".format(user_email_verification.email_token),
                to=[user.email],
            )
            email.send()
            user_email_verification.created_at = timezone.now()
            user_email_verification.save()

        return user
