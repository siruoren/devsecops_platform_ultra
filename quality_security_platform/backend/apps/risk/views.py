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


from django.http import JsonResponse


def get_risk_dashboard(request):
    """
    获取风险看板数据
    """
    if request.method == 'GET':
        try:
            # 查询所有风险档案
            risk_profiles = RiskProfile.objects.select_related('project').all()
            
            # 构建风险看板数据
            dashboard_data = {
                'total_projects': risk_profiles.count(),
                'high_risk_projects': risk_profiles.filter(overall_score__gte=70).count(),
                'medium_risk_projects': risk_profiles.filter(overall_score__gte=40, overall_score__lt=70).count(),
                'low_risk_projects': risk_profiles.filter(overall_score__lt=40).count(),
                'risk_trend': [],
                'project_risks': []
            }
            
            # 构建项目风险列表
            for profile in risk_profiles:
                project_risk = {
                    'project_id': profile.project.id,
                    'project_name': profile.project.name,
                    'overall_score': profile.overall_score,
                    'code_quality_score': profile.code_quality_score,
                    'vulnerability_score': profile.vulnerability_score,
                    'pipeline_score': profile.pipeline_score,
                    'risk_level': 'low'
                }
                
                # 确定风险等级
                if profile.overall_score >= 70:
                    project_risk['risk_level'] = 'high'
                elif profile.overall_score >= 40:
                    project_risk['risk_level'] = 'medium'
                
                dashboard_data['project_risks'].append(project_risk)
            
            # TODO: 构建风险趋势数据（需要历史数据）
            # 这里可以从数据库中查询历史风险评分数据，构建趋势图表
            
            return JsonResponse({'status': 'success', 'dashboard_data': dashboard_data})
        except Exception as e:
            print(f"获取风险看板数据失败: {e}")
            return JsonResponse({'status': 'error', 'message': '获取风险看板数据失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})
