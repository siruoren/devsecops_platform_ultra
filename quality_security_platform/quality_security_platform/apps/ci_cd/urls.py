from rest_framework.routers import SimpleRouter
from .views import PipelineViewSet, BuildRecordViewSet
router = SimpleRouter()
router.register('pipelines', PipelineViewSet, basename='pipeline')
router.register('builds', BuildRecordViewSet, basename='build')
urlpatterns = router.urls
