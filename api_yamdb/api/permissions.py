from rest_framework import permissions


class IsAuthorOrStaff(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user == obj.author
                or (request.user.is_moderator or request.user.is_admin))


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_admin
