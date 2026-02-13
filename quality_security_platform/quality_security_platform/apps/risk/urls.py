from rest_framework.routers import SimpleRouter
from .views import RiskProfileViewSet, RiskAlertViewSet
router = SimpleRouter()
router.register('profiles', RiskProfileViewSet, basename='riskprofile')
router.register('alerts', RiskAlertViewSet, basename='riskalert')
urlpatterns = router.urls
