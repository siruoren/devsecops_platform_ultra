from django.urls import path
from django.contrib.staticfiles.views import serve as static_serve
from django.views.generic import TemplateView
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views  # 导入认证视图
from django.views.generic import RedirectView
from django.contrib.auth.views import LogoutView
from django.contrib.staticfiles.views import serve
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="质量安全平台 API",
        default_version='v1.0',
        description="QSP 后端接口文档",
        contact=openapi.Contact(email="admin@example.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],  # 公开文档，无需登录
)


urlpatterns = [

    # 后台管理
    path('admin/', admin.site.urls),

    # 认证相关：注销（Logout）
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('accounts/logout/', LogoutView.as_view(next_page='/'), name='account_logout'),
    # API 路由
    path('api/users/', include('apps.users.urls')),
    path('api/projects/', include('apps.projects.urls')),
    path('api/versions/', include('apps.versions.urls')),
    path('api/vulnerabilities/', include('apps.vulnerabilities.urls')),
    path('api/system/', include('apps.system.urls')),
    path('api/rbac/', include('apps.rbac.urls')),
    path('api/cicd/', include('apps.ci_cd.urls')),
    path('api/risk/', include('apps.risk.urls')),

    # Swagger 文档
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('api/', RedirectView.as_view(url='/swagger/', permanent=False)),
    path('', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('users/', TemplateView.as_view(template_name='users.html'), name='users'),
    path('projects/', TemplateView.as_view(template_name='projects.html'), name='projects'),
    path('versions/', TemplateView.as_view(template_name='versions.html'), name='versions'),
    path('vulnerabilities/', TemplateView.as_view(template_name='vulnerabilities.html'), name='vulnerabilities'),
    path('cicd/', TemplateView.as_view(template_name='cicd.html'), name='cicd'),
    path('risk/', TemplateView.as_view(template_name='risk.html'), name='risk'),
    path('system/', TemplateView.as_view(template_name='system.html'), name='system'),
    # 静态文件服务（开发环境）
    path('static/<path:path>', static_serve),
]
