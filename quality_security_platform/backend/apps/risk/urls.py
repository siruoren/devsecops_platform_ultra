from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import RiskProfileViewSet, RiskAlertViewSet, get_risk_dashboard
router = SimpleRouter()
router.register('profiles', RiskProfileViewSet, basename='riskprofile')
router.register('alerts', RiskAlertViewSet, basename='riskalert')
urlpatterns = [
    # 获取风险看板数据
    path('dashboard/', get_risk_dashboard, name='get_risk_dashboard'),
]
urlpatterns += router.urls
