from rest_framework.routers import SimpleRouter
from .views import ProjectViewSet, EnvironmentViewSet
router = SimpleRouter()
router.register('projects', ProjectViewSet, basename='project')
router.register('environments', EnvironmentViewSet, basename='environment')
urlpatterns = router.urls
