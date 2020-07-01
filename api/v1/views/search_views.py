from rest_framework import generics, permissions, exceptions
from rest_framework.response import Response

from django.contrib.postgres.search import SearchVector

from api.v1.serializers.edit_profile_serializers import UserProfileSerializer

from users.models import UserProfile


class UserSearchList(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(search=SearchVector("user__first_name", "user__last_name"),)
            .filter(search=self.request.query_params.get("keywords"))
        )

    def list(self, request, *args, **kwargs):
        if self.get_queryset():
            serializer = self.get_serializer(self.get_queryset(), many=True)
            return Response(serializer.data)

        raise exceptions.NotFound()
