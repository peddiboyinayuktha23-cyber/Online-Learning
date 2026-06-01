from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == "ADMIN"


class IsInstructorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in {"INSTRUCTOR", "ADMIN"}


class IsOwnerInstructorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.role == "ADMIN" or user.is_staff:
            return True
        owner = getattr(obj, "student", None) or getattr(obj, "user", None)
        if owner == user:
            return True
        course = getattr(obj, "course", None)
        return course is not None and getattr(course, "instructor_id", None) == user.id
