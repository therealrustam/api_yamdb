from rest_framework import permissions

from reviews.models import Comment, Review


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_superuser
                 or request.user.is_admin)
        )


class AdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin


class ReviewCommentPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and request.user.is_admin:
            return True
        if ((type(obj) == Comment or type(obj) == Review)
            and request.user.is_authenticated
                and request.user.is_moderator):
            return True
        return (obj.author == request.user
                or request.method in permissions.SAFE_METHODS)
