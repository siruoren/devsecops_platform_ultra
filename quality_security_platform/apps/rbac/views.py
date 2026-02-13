from rest_framework import viewsets
from .models import Permission, Role, UserRole
from .serializers import *
from apps.base.viewsets import BaseModelViewSet
class PermissionViewSet(BaseModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
class RoleViewSet(BaseModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
class UserRoleViewSet(BaseModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
