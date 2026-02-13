from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project, Environment
from .serializers import ProjectSerializer, EnvironmentSerializer
from apps.base.viewsets import BaseModelViewSet
class ProjectViewSet(BaseModelViewSet):
    queryset = Project.objects.select_related('environment', 'owner').all()
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name', 'environment']
    search_fields = ['name', 'git_repo']
class EnvironmentViewSet(BaseModelViewSet):
    queryset = Environment.objects.all()
    serializer_class = EnvironmentSerializer
