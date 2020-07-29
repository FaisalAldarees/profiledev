from rest_framework import permissions, generics, status
from rest_framework.response import Response


class HelthView(generics.RetrieveAPIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def retrieve(self, request, *args, **kwargs):
        return Response({"success": True}, status=status.HTTP_200_OK)
