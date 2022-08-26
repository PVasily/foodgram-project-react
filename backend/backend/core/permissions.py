from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthOrReadOnly(BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )


class IsAuthOrAdmin(BasePermission):
    """
    Only authorised users.
    """
    def has_permission(self, request, view):
        return (
                request.user.is_authenticated
                or request.user.is_admin
        )

    def has_object_permission(self, request, view, obj):
        return obj.author or request.user.is_admin   


class IsAuthAndAuthorOrReadOnly(BasePermission):
    """
    Only authorised and authors.
    """
    def has_permission(self, request, view):
        print(request.user)
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        print(obj.author == request.user)
        return (
            request.method in SAFE_METHODS
            or (
                request.user.is_authenticated
                and obj.author == request.user
            )
        )
