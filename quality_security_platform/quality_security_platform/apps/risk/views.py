from rest_framework import viewsets
from .models import RiskProfile, RiskAlert
from .serializers import RiskProfileSerializer, RiskAlertSerializer
from apps.base.viewsets import BaseModelViewSet
class RiskProfileViewSet(BaseModelViewSet):
    queryset = RiskProfile.objects.select_related('project').all()
    serializer_class = RiskProfileSerializer
class RiskAlertViewSet(BaseModelViewSet):
    queryset = RiskAlert.objects.select_related('project').all()
    serializer_class = RiskAlertSerializer
