from rest_framework.settings import api_settings
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import permissions

from api.v1.serializers.login_serializers import AuthTokenSerializer


class CreateTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)
