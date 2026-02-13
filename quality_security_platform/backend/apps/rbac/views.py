from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Permission, Role, UserRole
from .serializers import *
from apps.base.viewsets import BaseModelViewSet


class PermissionViewSet(BaseModelViewSet):
    """
    权限管理：支持过滤、搜索、排序、批量删除
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code', 'module', 'is_menu']
    search_fields = ['code', 'name', 'module']
    ordering_fields = ['id', 'code', 'module']

    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        if not request.user.is_superuser:
            return Response({'detail': '无权限'}, status=status.HTTP_403_FORBIDDEN)
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'detail': '请提供要删除的ID列表'}, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = self.get_queryset().filter(id__in=ids).delete()
        return Response({'deleted': deleted}, status=status.HTTP_200_OK)


class RoleViewSet(BaseModelViewSet):
    """
    角色管理：支持过滤、搜索、排序、批量删除
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'code']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['id', 'name', 'code']

    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        if not request.user.is_superuser:
            return Response({'detail': '无权限'}, status=status.HTTP_403_FORBIDDEN)
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'detail': '请提供要删除的ID列表'}, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = self.get_queryset().filter(id__in=ids).delete()
        return Response({'deleted': deleted}, status=status.HTTP_200_OK)


class UserRoleViewSet(BaseModelViewSet):
    """
    用户角色分配：支持批量删除（超级管理员）
    """
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'role']
    search_fields = ['user__username', 'role__name']
    ordering_fields = ['id', 'created_at']

    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        if not request.user.is_superuser:
            return Response({'detail': '无权限'}, status=status.HTTP_403_FORBIDDEN)
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'detail': '请提供要删除的ID列表'}, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = self.get_queryset().filter(id__in=ids).delete()
        return Response({'deleted': deleted}, status=status.HTTP_200_OK)