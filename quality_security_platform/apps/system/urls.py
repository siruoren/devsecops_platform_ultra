from rest_framework.routers import DefaultRouter
from .views import SystemConfigViewSet, NotificationViewSet
router = DefaultRouter()
router.register('config', SystemConfigViewSet)
router.register('notifications', NotificationViewSet)
urlpatterns = router.urls
