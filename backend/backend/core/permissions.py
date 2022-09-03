from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthOrReadOnly(BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )


class IsAuthor(BasePermission):
    """
    Only authorised users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        print(obj.author)
        return obj.author == request.user


class IsAuthAndAuthorOrReadOnly(BasePermission):
    """
    Only authorised and authors.
    """
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or (
                request.user.is_authenticated
                and obj.author == request.user
            )
        )
