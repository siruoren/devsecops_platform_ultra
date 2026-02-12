from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, EnvironmentViewSet
router = DefaultRouter()
router.register('projects', ProjectViewSet)
router.register('environments', EnvironmentViewSet)
urlpatterns = router.urls
