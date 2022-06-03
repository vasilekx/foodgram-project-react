# api/permissions.py

from rest_framework.permissions import (
    BasePermission, SAFE_METHODS
)


class IsAdministrator(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdministratorOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated
                and request.user.is_admin)
