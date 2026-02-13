from rest_framework import viewsets, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Pipeline, BuildRecord
from .serializers import PipelineSerializer, BuildRecordSerializer
from apps.base.viewsets import BaseModelViewSet


class PipelineViewSet(BaseModelViewSet):
    """
    流水线定义：支持过滤、搜索、排序、批量删除
    """
    queryset = Pipeline.objects.all()
    serializer_class = PipelineSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'project', 'is_active']
    search_fields = ['name', 'description', 'project__name']
    ordering_fields = ['id', 'name', 'created_at']

    @action(detail=True, methods=['post'])
    def trigger(self, request, pk=None):
        pipeline = self.get_object()
        version = request.data.get('version', 'main')
        # 此处应触发 Celery 任务，现简化返回
        return Response({'status': 'triggered', 'pipeline_id': pipeline.id, 'version': version})

    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        if not request.user.is_superuser:
            return Response({'detail': '无权限'}, status=status.HTTP_403_FORBIDDEN)
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'detail': '请提供要删除的ID列表'}, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = self.get_queryset().filter(id__in=ids).delete()
        return Response({'deleted': deleted}, status=status.HTTP_200_OK)


class BuildRecordViewSet(BaseModelViewSet):
    """
    构建记录：支持过滤、搜索、排序、批量删除
    """
    queryset = BuildRecord.objects.all()
    serializer_class = BuildRecordSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['pipeline', 'status', 'triggered_by']
    search_fields = ['build_id', 'version', 'pipeline__name']
    ordering_fields = ['id', 'created_at', 'duration', 'started_at']

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        build = self.get_object()
        if build.status in ['pending', 'running']:
            build.status = 'aborted'
            build.finished_at = timezone.now()
            build.save()
            return Response({'status': 'cancelled'})
        return Response({'error': '无法取消'}, status=400)

    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        if not request.user.is_superuser:
            return Response({'detail': '无权限'}, status=status.HTTP_403_FORBIDDEN)
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'detail': '请提供要删除的ID列表'}, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = self.get_queryset().filter(id__in=ids).delete()
        return Response({'deleted': deleted}, status=status.HTTP_200_OK)