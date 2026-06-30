"""Role-based permission classes reused across the API."""
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Allow access only to admin or super admin users."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_admin
        )


class IsSuperAdmin(BasePermission):
    """Allow access only to super admin users."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == request.user.Role.SUPER_ADMIN
        )


class IsAdminOrOwner(BasePermission):
    """Allow any authenticated user; restrict objects to admins or owners.

    Listing is scoped per user in each view's ``get_queryset``; this class is
    the object-level defense. Admins access everything. Clients only reach an
    object they own. The owner of an object is resolved by the view through a
    ``get_object_owner(obj)`` method (returns the owning ``User`` or ``None``).
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if getattr(request.user, "is_admin", False):
            return True
        get_owner = getattr(view, "get_object_owner", None)
        if get_owner is None:
            return False
        return get_owner(obj) == request.user
