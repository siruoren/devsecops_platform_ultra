from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.staticfiles.views import serve
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="质量安全平台 API",
        default_version='v3.0',
        description="QSP 全功能接口文档",
        contact=openapi.Contact(email="admin@example.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('', RedirectView.as_view(url='/swagger/', permanent=False)),  # 首页重定向
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/projects/', include('apps.projects.urls')),
    path('api/versions/', include('apps.versions.urls')),
    path('api/vulnerabilities/', include('apps.vulnerabilities.urls')),
    path('api/system/', include('apps.system.urls')),
    path('api/rbac/', include('apps.rbac.urls')),
    path('api/cicd/', include('apps.ci_cd.urls')),
    path('api/risk/', include('apps.risk.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^favicon\.ico$', serve, {'path': 'favicon.ico'}),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)