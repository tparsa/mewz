from rest_framework.permissions import BasePermission

from mafia_django import settings


class IsNotAuthenticated(BasePermission):
    """
    Allows access only to not authenticated users.
    """

    def has_permission(self, request, view):
        return not bool(request.user and request.user.is_authenticated)


class ServerUserOnly(BasePermission):
    def has_permission(self, request, view):
        try:
            return request.headers['Token'] == settings.SERVER_TOKEN
        except KeyError:
            return False
