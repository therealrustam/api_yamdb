from rest_framework import permissions


class ModeratorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.role == 'moderator'
        )

    def has_object_permission(self, request, view, obj):
        return request.user.role == 'moderator'
