from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            # Allow librarian to access
            if not hasattr(request.user, 'user_role'):
                return False

            if request.user.user_role.role == 'LIBRARIAN':
                return True

            # Only allow owners to modify their own objects
            if hasattr(obj, 'owner'):
                return obj.owner == request.user
        except AttributeError:
            return False
        return False


class StudentPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            if request.user.user_role.role == 'STUDENT':
                return True
        except AttributeError:
            return False
        return False


class LibrarianPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            if request.user.user_role.role == 'LIBRARIAN':
                return True
        except AttributeError:
            pass
        return False
