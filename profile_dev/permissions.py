from rest_framework.permissions import BasePermission


class IsEmailVerified(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_email_verified)