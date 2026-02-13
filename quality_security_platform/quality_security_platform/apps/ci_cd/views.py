from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Pipeline, BuildRecord
from .serializers import PipelineSerializer, BuildRecordSerializer
from apps.base.viewsets import BaseModelViewSet
class PipelineViewSet(BaseModelViewSet):
    queryset = Pipeline.objects.all()
    serializer_class = PipelineSerializer
    @action(detail=True, methods=['post'])
    def trigger(self, request, pk=None):
        pipeline = self.get_object()
        version = request.data.get('version', 'main')
        # 触发构建逻辑 (Celery任务)
        from .tasks import run_pipeline
        task = run_pipeline.delay(pipeline.id, version, request.user.id)
        return Response({'task_id': task.id, 'status': 'triggered'})
class BuildRecordViewSet(BaseModelViewSet):
    queryset = BuildRecord.objects.all()
    serializer_class = BuildRecordSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['pipeline__name', 'version', 'build_id']
    ordering_fields = ['created_at', 'duration']
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        build = self.get_object()
        if build.status in ['pending', 'running']:
            build.status = 'aborted'
            build.finished_at = timezone.now()
            build.save()
            return Response({'status': 'cancelled'})
        return Response({'error': '无法取消'}, status=400)
