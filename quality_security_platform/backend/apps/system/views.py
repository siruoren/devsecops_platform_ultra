from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Notification
from .serializers import NotificationSerializer
from apps.base.viewsets import BaseModelViewSet


class NotificationViewSet(BaseModelViewSet):
    """
    通知管理：支持过滤、搜索、排序、批量删除（仅自己的通知）
    """
    serializer_class = NotificationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_read']
    search_fields = ['title', 'content']
    ordering_fields = ['id', 'created_at']

    def get_queryset(self):
        # 仅返回当前用户的通知
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response({'status': 'ok'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})

    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        """
        批量删除自己的通知（仅已读通知，或所有通知）
        """
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'detail': '请提供要删除的ID列表'}, status=status.HTTP_400_BAD_REQUEST)
        # 仅删除属于当前用户的通知，防止越权
        qs = self.get_queryset().filter(id__in=ids)
        deleted, _ = qs.delete()
        return Response({'deleted': deleted}, status=status.HTTP_200_OK)