from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import SimpleRouter
from .views import UserViewSet

# 创建路由器（用于除登录外的其他动作）
router = SimpleRouter()
router.register('', UserViewSet, basename='user')

# 手动创建登录视图并应用 csrf_exempt
login_view = UserViewSet.as_view({'post': 'login'})

# 手动路由放在 router.urls 之前，确保优先匹配
urlpatterns = [
    path('login/', csrf_exempt(login_view), name='user-login'),
] + router.urls