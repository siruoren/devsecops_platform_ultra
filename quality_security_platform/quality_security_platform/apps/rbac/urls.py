from rest_framework.routers import SimpleRouter
from .views import PermissionViewSet, RoleViewSet, UserRoleViewSet
router = SimpleRouter()
router.register('permissions', PermissionViewSet, basename='permission')
router.register('roles', RoleViewSet, basename='role')
router.register('user-roles', UserRoleViewSet, basename='userrole')
urlpatterns = router.urls
