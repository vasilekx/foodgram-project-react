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


class IsOwnerOrReadOnly(BasePermission):
    """
    Разрешение на уровне объекта, позволяющее редактировать объект только
    владельцам. Предполагается, что экземпляр модели имеет атрибут `author`.
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
        )
