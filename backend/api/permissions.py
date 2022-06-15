# api/permissions.py

from rest_framework.permissions import (
    BasePermission, SAFE_METHODS, IsAuthenticatedOrReadOnly
)


# class IsAdministrator(BasePermission):
#
#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user.is_admin
#
#
# class IsAdministratorOrReadOnly(BasePermission):
#
#     def has_permission(self, request, view):
#         return (request.method in SAFE_METHODS
#                 or request.user.is_authenticated
#                 and request.user.is_admin)


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


class IsOwner(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # r1 = request.user.is_owner(obj)
        # r2 = obj.author == request.user
        return (
            request.user
            and request.user.is_authenticated
            and obj.author == request.user
            # and request.user.is_owner(obj)
        )
