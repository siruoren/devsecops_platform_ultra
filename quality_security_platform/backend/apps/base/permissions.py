from rest_framework.permissions import BasePermission, SAFE_METHODS
class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS: return True
        return request.user and request.user.is_superuser
class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser: return True
        if hasattr(obj, 'created_by'): return obj.created_by == request.user
        if hasattr(obj, 'owner'): return obj.owner == request.user
        return False
