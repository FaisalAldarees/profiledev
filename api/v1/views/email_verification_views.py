from rest_framework import permissions, generics

from api.v1.serializers.registration_serializers import UserSerializer

from users.models import UserEmailVerification


class VerifyEmail(generics.RetrieveAPIView):
    model = UserEmailVerification
    queryset = UserEmailVerification.objects.all()
    serializer_class = UserSerializer
    lookup_field = "email_token"
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def get_object(self):
        user = UserEmailVerification.objects.get(
            email_token=self.kwargs["email_token"]
        ).user
        user.is_active = True
        user.save()
        return user
