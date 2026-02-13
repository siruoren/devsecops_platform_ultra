from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Project, Environment
from .serializers import ProjectSerializer, EnvironmentSerializer
from apps.base.viewsets import BaseModelViewSet


class ProjectViewSet(BaseModelViewSet):
    """
    项目管理：支持过滤、搜索、排序、批量删除
    """
    queryset = Project.objects.select_related('environment', 'owner').all()
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'environment', 'owner']
    search_fields = ['name', 'git_repo', 'deploy_dir']
    ordering_fields = ['id', 'name', 'created_at', 'updated_at']

    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        if not request.user.is_superuser:
            return Response({'detail': '无权限'}, status=status.HTTP_403_FORBIDDEN)
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'detail': '请提供要删除的ID列表'}, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = self.get_queryset().filter(id__in=ids).delete()
        return Response({'deleted': deleted}, status=status.HTTP_200_OK)


class EnvironmentViewSet(BaseModelViewSet):
    """
    环境管理：支持过滤、搜索、排序、批量删除
    """
    queryset = Environment.objects.all()
    serializer_class = EnvironmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name']
    search_fields = ['name', 'server_ips']
    ordering_fields = ['id', 'name', 'created_at']

    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        if not request.user.is_superuser:
            return Response({'detail': '无权限'}, status=status.HTTP_403_FORBIDDEN)
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'detail': '请提供要删除的ID列表'}, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = self.get_queryset().filter(id__in=ids).delete()
        return Response({'deleted': deleted}, status=status.HTTP_200_OK)