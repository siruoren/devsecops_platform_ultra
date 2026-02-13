from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import RiskProfile, RiskAlert
from .serializers import RiskProfileSerializer, RiskAlertSerializer
from apps.base.viewsets import BaseModelViewSet


class RiskProfileViewSet(BaseModelViewSet):
    """
    风险档案：支持过滤、搜索、排序、批量删除
    """
    queryset = RiskProfile.objects.select_related('project').all()
    serializer_class = RiskProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'overall_score']
    search_fields = ['project__name']
    ordering_fields = ['id', 'overall_score', 'updated_at']

    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        if not request.user.is_superuser:
            return Response({'detail': '无权限'}, status=status.HTTP_403_FORBIDDEN)
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'detail': '请提供要删除的ID列表'}, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = self.get_queryset().filter(id__in=ids).delete()
        return Response({'deleted': deleted}, status=status.HTTP_200_OK)


class RiskAlertViewSet(BaseModelViewSet):
    """
    风险告警：支持过滤、搜索、排序、批量删除
    """
    queryset = RiskAlert.objects.select_related('project').all()
    serializer_class = RiskAlertSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'level', 'is_resolved']
    search_fields = ['title', 'description', 'project__name']
    ordering_fields = ['id', 'created_at', 'level']

    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        if not request.user.is_superuser:
            return Response({'detail': '无权限'}, status=status.HTTP_403_FORBIDDEN)
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'detail': '请提供要删除的ID列表'}, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = self.get_queryset().filter(id__in=ids).delete()
        return Response({'deleted': deleted}, status=status.HTTP_200_OK)