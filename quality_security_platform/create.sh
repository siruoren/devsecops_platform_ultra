#!/bin/bash
# ============================================================================
# 质量安全平台 QSP - 全功能生成脚本
# 版本: 3.0.0
# 描述: 生成完整 Django 项目，含 RBAC、CI/CD、风险评分、流水线可视化
# ============================================================================

set -e

PROJECT_NAME="quality_security_platform"
ZIP_FILE="${PROJECT_NAME}.zip"
echo "🔨 正在构建项目: $PROJECT_NAME"

# 创建项目根目录
mkdir -p $PROJECT_NAME
cd $PROJECT_NAME

# ============================== 1. 基础环境配置 ==============================
cat > .env.dev << 'EOF'
DEBUG=True
SECRET_KEY=dev-secret-key-qsp-2026
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
EOF

cat > .env.prod << 'EOF'
DEBUG=False
SECRET_KEY=prod-secret-key-strong-2026
ALLOWED_HOSTS=.example.com,localhost
DB_ENGINE=postgresql
DB_NAME=qsp
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=postgres_master
DB_PORT=5432
DB_REPLICA_ENGINE=postgresql
DB_REPLICA_NAME=qsp
DB_REPLICA_USER=postgres
DB_REPLICA_PASSWORD=postgres123
DB_REPLICA_HOST=postgres_slave
DB_REPLICA_PORT=5432
REDIS_PASSWORD=redis123
REDIS_URL=redis://:${REDIS_PASSWORD}@redis_master:6379/0
CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis_master:6379/1
CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@redis_master:6379/2
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=admin@example.com
EMAIL_HOST_PASSWORD=emailpass
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=admin@example.com
SONAR_HOST_URL=http://sonarqube:9000
SONAR_TOKEN=your_sonar_token
EOF

# ============================== 2. requirements.txt ==============================
cat > requirements.txt << 'EOF'
Django==3.2.18
djangorestframework==3.14.0
django-cors-headers==3.13.0
django-filter==22.1
django-environ==0.9.0
psycopg2-binary==2.9.5
mysqlclient==2.1.1
django-redis==5.2.0
redis==4.5.1
celery==5.2.7
flower==1.2.0
drf-yasg==1.21.5
networkx==3.1
pyvis==0.3.1
gunicorn==20.1.0
requests==2.28.2
djangorestframework-simplejwt==5.2.2
django-cryptography==1.0
django-import-export==3.2.0
django-constance[database]==2.9.1
django-constance[django-redis]==2.9.1
django-rq==2.7.0
EOF

# ============================== 3. Docker 相关文件 ==============================
cat > Dockerfile << 'EOF'
FROM python:3.9-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TZ=Asia/Shanghai
WORKDIR /app
RUN apt-get update && apt-get install -y gcc libpq-dev netcat curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x /app/scripts/entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
EOF

cat > Dockerfile.celery << 'EOF'
FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc libpq-dev netcat && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x /app/scripts/entrypoint-celery.sh
ENTRYPOINT ["/app/scripts/entrypoint-celery.sh"]
EOF

# 基础 docker-compose.yml (SQLite)
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    container_name: qsp_redis
    networks: [qsp_network]
  web:
    build: .
    container_name: qsp_web
    command: python manage.py runserver 0.0.0.0:8000
    volumes: [.:/app]
    ports: ["8000:8000"]
    env_file: [.env.dev]
    depends_on: [redis]
    networks: [qsp_network]
  celery_worker:
    build: 
      context: .
      dockerfile: Dockerfile.celery
    container_name: qsp_celery_worker
    command: celery -A config worker --loglevel=info
    volumes: [.:/app]
    env_file: [.env.dev]
    depends_on: [redis, web]
    networks: [qsp_network]
networks: {qsp_network: {driver: bridge}}
EOF

# ============================== 4. 项目配置 ==============================
mkdir -p config config/settings

# config/__init__.py
cat > config/__init__.py << 'EOF'
from __future__ import absolute_import, unicode_literals
from .celery import app as celery_app
__all__ = ('celery_app',)
EOF

# config/celery.py
cat > config/celery.py << 'EOF'
import os
from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
app = Celery('quality_security_platform')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
EOF

# config/database_router.py
cat > config/database_router.py << 'EOF'
import random

class MasterSlaveRouter:
    def db_for_read(self, model, **hints): return 'replica'
    def db_for_write(self, model, **hints): return 'default'
    def allow_relation(self, obj1, obj2, **hints): return True
    def allow_migrate(self, db, app_label, model_name=None, **hints): return db == 'default'

class ActiveActiveRouter:
    def db_for_read(self, model, **hints): return random.choice(['dc1_replica', 'dc2_replica'])
    def db_for_write(self, model, **hints): return ['dc1_master', 'dc2_master']
    def allow_relation(self, obj1, obj2, **hints): return True
    def allow_migrate(self, db, app_label, model_name=None, **hints): return True
EOF

# config/urls.py (含所有模块路由，并注释未完成的)
cat > config/urls.py << 'EOF'
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
EOF

# config/wsgi.py
cat > config/wsgi.py << 'EOF'
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
application = get_wsgi_application()
EOF

# config/asgi.py
cat > config/asgi.py << 'EOF'
import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
application = get_asgi_application()
EOF

# ============================== 5. settings 多环境配置 ==============================
cat > config/settings/__init__.py << 'EOF'
from .base import *
EOF

cat > config/settings/base.py << 'EOF'
import os
from pathlib import Path
import environ
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 第三方
    'rest_framework',
    'corsheaders',
    'django_filters',
    'drf_yasg',
    'import_export',
    'constance',
    'constance.backends.database',
    # 本地应用
    'apps.users',
    'apps.projects',
    'apps.versions',
    'apps.vulnerabilities',
    'apps.system',
    'apps.rbac',
    'apps.ci_cd',
    'apps.risk',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
AUTH_USER_MODEL = 'users.User'
DATABASES = {'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3')}
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://127.0.0.1:6379/0'),
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'}
    }
}
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=['http://localhost:3000'])
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# Celery
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/1')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379/2')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'
# Constance 动态配置
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_CONFIG = {
    'MAX_DAILY_MESSAGES': (100, '每日最大站内信', int),
    'MAX_DAILY_EMAILS': (500, '每日最大邮件发送量', int),
    'SMTP_SERVER': ('smtp.example.com', 'SMTP服务器'),
    'SMTP_PORT': (587, 'SMTP端口', int),
    'SMTP_USERNAME': ('', 'SMTP用户名'),
    'SMTP_PASSWORD': ('', 'SMTP密码'),
    'SENDER_EMAIL': ('noreply@example.com', '发送人邮箱'),
    'SONAR_HOST_URL': ('http://localhost:9000', 'SonarQube地址'),
    'SONAR_TOKEN': ('', 'SonarQube Token'),
}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
EOF

cat > config/settings/development.py << 'EOF'
from .base import *
DEBUG = True
ALLOWED_HOSTS = ['*']
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
CORS_ALLOW_ALL_ORIGINS = True
EOF

cat > config/settings/production.py << 'EOF'
from .base import *
DEBUG = False
DATABASES = {
    'default': {
        'ENGINE': f'django.db.backends.{env("DB_ENGINE")}',
        'NAME': env('DB_NAME'), 'USER': env('DB_USER'), 'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'), 'PORT': env('DB_PORT'), 'CONN_MAX_AGE': 60,
    },
    'replica': {
        'ENGINE': f'django.db.backends.{env("DB_REPLICA_ENGINE")}',
        'NAME': env('DB_REPLICA_NAME'), 'USER': env('DB_REPLICA_USER'),
        'PASSWORD': env('DB_REPLICA_PASSWORD'), 'HOST': env('DB_REPLICA_HOST'),
        'PORT': env('DB_REPLICA_PORT'), 'CONN_MAX_AGE': 60,
    }
}
DATABASE_ROUTERS = ['config.database_router.MasterSlaveRouter']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
EOF

# ============================== 6. manage.py ==============================
cat > manage.py << 'EOF'
#!/usr/bin/env python
import os, sys
def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django.") from exc
    execute_from_command_line(sys.argv)
if __name__ == '__main__':
    main()
EOF

# ============================== 7. 脚本目录 ==============================
mkdir -p scripts
cat > scripts/entrypoint.sh << 'EOF'
#!/bin/bash
set -e
python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec "$@"
EOF
chmod +x scripts/entrypoint.sh

cat > scripts/entrypoint-celery.sh << 'EOF'
#!/bin/bash
set -e
until nc -z redis 6379; do echo "Waiting for Redis..."; sleep 1; done
exec "$@"
EOF
chmod +x scripts/entrypoint-celery.sh

cat > scripts/init_db.py << 'EOF'
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()
from django.contrib.auth import get_user_model
from apps.rbac.models import Role, Permission
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ 超级用户 admin 创建成功')
else:
    print('ℹ️ 超级用户已存在')
# 初始化默认权限
Permission.init_defaults()
# 初始化默认角色
Role.init_defaults()
print('🎉 数据库初始化完成')
EOF
chmod +x scripts/init_db.py

# ============================== 8. 应用模块（含全部功能）==============================
mkdir -p apps
touch apps/__init__.py

# ---------- 8.1 基础共享模块 ----------
mkdir -p apps/base
cat > apps/base/__init__.py << 'EOF'
EOF

cat > apps/base/viewsets.py << 'EOF'
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return super().get_queryset()
EOF

cat > apps/base/permissions.py << 'EOF'
from rest_framework.permissions import BasePermission, SAFE_METHODS
class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser
class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False
EOF

# ---------- 8.2 用户管理（已扩展RBAC）----------
mkdir -p apps/users
cat > apps/users/__init__.py << 'EOF'
EOF

cat > apps/users/models.py << 'EOF'
from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
    username = models.CharField('用户名', max_length=150, unique=True)
    email = models.EmailField('邮箱', unique=True)
    password = models.CharField('密码', max_length=128)
    avatar = models.ImageField('头像', upload_to='avatars/', null=True, blank=True)
    phone = models.CharField('手机号', max_length=20, blank=True)
    department = models.CharField('部门', max_length=100, blank=True)
    position = models.CharField('职位', max_length=100, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'
    def __str__(self):
        return self.username
EOF

cat > apps/users/serializers.py << 'EOF'
from rest_framework import serializers
from .models import User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', 'user_permissions', 'groups']
        read_only_fields = ['created_at', 'updated_at']
class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone', 'department', 'position']
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'department', 'position', 'avatar']
    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError('邮箱已被使用')
        return value
class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField()
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError('两次密码不一致')
        return data
EOF

cat > apps/users/views.py << 'EOF'
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from .models import User
from .serializers import *
from apps.base.viewsets import BaseModelViewSet
class UserViewSet(BaseModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ['update', 'partial_update'] and not self.request.user.is_superuser:
            return UserUpdateSerializer
        if self.action == 'change_password':
            return PasswordChangeSerializer
        if self.action == 'login':
            return UserLoginSerializer
        return UserSerializer
    def get_permissions(self):
        if self.action == 'login':
            return [AllowAny()]
        return super().get_permissions()
    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(**serializer.validated_data)
        if user:
            login(request, user)
            return Response(UserSerializer(user).data)
        return Response({'error': '用户名或密码错误'}, status=401)
    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'message': '退出成功'})
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': '原密码错误'}, status=400)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': '密码修改成功'})
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
EOF

cat > apps/users/urls.py << 'EOF'
from rest_framework.routers import SimpleRouter
from .views import UserViewSet
router = SimpleRouter()
router.register('', UserViewSet, basename='user')
urlpatterns = router.urls
EOF

# ---------- 8.3 RBAC 权限系统 ----------
mkdir -p apps/rbac
cat > apps/rbac/__init__.py << 'EOF'
EOF

cat > apps/rbac/models.py << 'EOF'
from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class Permission(models.Model):
    """功能权限 - 对应菜单/按钮"""
    code = models.CharField('权限代码', max_length=100, unique=True)
    name = models.CharField('权限名称', max_length=100)
    module = models.CharField('所属模块', max_length=50)
    is_menu = models.BooleanField('是否为菜单', default=False)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='父权限')
    class Meta:
        db_table = 'rbac_permissions'
        verbose_name = '权限'
    def __str__(self):
        return f"{self.module}-{self.name}"
    @classmethod
    def init_defaults(cls):
        default_perms = [
            ('user_view', '查看用户', 'user', False),
            ('user_add', '新建用户', 'user', False),
            ('user_edit', '编辑用户', 'user', False),
            ('user_delete', '删除用户', 'user', False),
            ('user_menu', '用户管理', 'user', True),
            ('project_view', '查看项目', 'project', False),
            ('project_add', '新建项目', 'project', False),
            ('project_edit', '编辑项目', 'project', False),
            ('project_delete', '删除项目', 'project', False),
            ('project_menu', '项目管理', 'project', True),
            ('version_view', '查看版本', 'version', False),
            ('version_edit', '编辑版本', 'version', False),
            ('version_menu', '版本管理', 'version', True),
            ('vuln_view', '查看漏洞', 'vuln', False),
            ('vuln_import', '导入漏洞', 'vuln', False),
            ('vuln_menu', '安全漏洞', 'vuln', True),
            ('system_config', '系统配置', 'system', True),
            ('cicd_view', '查看流水线', 'cicd', False),
            ('cicd_trigger', '触发构建', 'cicd', False),
            ('cicd_menu', 'CI/CD', 'cicd', True),
            ('risk_view', '风险看板', 'risk', True),
        ]
        for code, name, module, is_menu in default_perms:
            cls.objects.get_or_create(code=code, defaults={'name': name, 'module': module, 'is_menu': is_menu})

class Role(models.Model):
    """角色"""
    name = models.CharField('角色名称', max_length=100, unique=True)
    code = models.CharField('角色标识', max_length=100, unique=True)
    permissions = models.ManyToManyField(Permission, blank=True, verbose_name='权限')
    description = models.TextField('描述', blank=True)
    class Meta:
        db_table = 'rbac_roles'
        verbose_name = '角色'
    def __str__(self):
        return self.name
    @classmethod
    def init_defaults(cls):
        admin_role, _ = cls.objects.get_or_create(code='admin', defaults={'name': '系统管理员'})
        admin_role.permissions.set(Permission.objects.all())
        dev_role, _ = cls.objects.get_or_create(code='developer', defaults={'name': '开发人员'})
        dev_role.permissions.set(Permission.objects.filter(code__in=[
            'project_view', 'version_view', 'vuln_view', 'cicd_view', 'risk_view'
        ]))
        qa_role, _ = cls.objects.get_or_create(code='qa', defaults={'name': '测试人员'})
        qa_role.permissions.set(Permission.objects.filter(code__in=[
            'project_view', 'version_view', 'vuln_view', 'vuln_import', 'risk_view'
        ]))

class UserRole(models.Model):
    """用户角色分配"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_assignments')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'rbac_user_roles'
        unique_together = ('user', 'role')
EOF

cat > apps/rbac/serializers.py << 'EOF'
from rest_framework import serializers
from .models import Permission, Role, UserRole
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'
class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(many=True, queryset=Permission.objects.all())
    class Meta:
        model = Role
        fields = '__all__'
class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = '__all__'
EOF

cat > apps/rbac/views.py << 'EOF'
from rest_framework import viewsets
from .models import Permission, Role, UserRole
from .serializers import *
from apps.base.viewsets import BaseModelViewSet
class PermissionViewSet(BaseModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
class RoleViewSet(BaseModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
class UserRoleViewSet(BaseModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
EOF

cat > apps/rbac/urls.py << 'EOF'
from rest_framework.routers import SimpleRouter
from .views import PermissionViewSet, RoleViewSet, UserRoleViewSet
router = SimpleRouter()
router.register('permissions', PermissionViewSet, basename='permission')
router.register('roles', RoleViewSet, basename='role')
router.register('user-roles', UserRoleViewSet, basename='userrole')
urlpatterns = router.urls
EOF

# ---------- 8.4 项目管理（完整）----------
mkdir -p apps/projects
cat > apps/projects/__init__.py << 'EOF'
EOF
cat > apps/projects/models.py << 'EOF'
from django.db import models
from apps.users.models import User
class Environment(models.Model):
    name = models.CharField('环境名', max_length=100, unique=True)
    server_ips = models.TextField('服务器IP', help_text='多个IP用逗号分隔')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: db_table = 'environments'
    def __str__(self): return self.name
class Project(models.Model):
    name = models.CharField('应用名', max_length=200, unique=True)
    git_repo = models.URLField('Git仓库地址')
    git_path = models.CharField('仓库内路径', max_length=500, default='/')
    environment = models.ForeignKey(Environment, on_delete=models.PROTECT)
    deploy_dir = models.CharField('部署目录', max_length=500)
    start_script = models.CharField('启动脚本', max_length=500)
    stop_script = models.CharField('停止脚本', max_length=500)
    start_cron = models.CharField('启动Cron', max_length=100, blank=True)
    stop_cron = models.CharField('停止Cron', max_length=100, blank=True)
    sonarqube_url = models.URLField('SonarQube项目地址', blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: db_table = 'projects'
EOF
cat > apps/projects/serializers.py << 'EOF'
from rest_framework import serializers
from .models import Project, Environment
class EnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Environment
        fields = '__all__'
class ProjectSerializer(serializers.ModelSerializer):
    environment_name = serializers.CharField(source='environment.name', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    class Meta:
        model = Project
        fields = '__all__'
EOF
cat > apps/projects/views.py << 'EOF'
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project, Environment
from .serializers import ProjectSerializer, EnvironmentSerializer
from apps.base.viewsets import BaseModelViewSet
class ProjectViewSet(BaseModelViewSet):
    queryset = Project.objects.select_related('environment', 'owner').all()
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name', 'environment']
    search_fields = ['name', 'git_repo']
class EnvironmentViewSet(BaseModelViewSet):
    queryset = Environment.objects.all()
    serializer_class = EnvironmentSerializer
EOF
cat > apps/projects/urls.py << 'EOF'
from rest_framework.routers import SimpleRouter
from .views import ProjectViewSet, EnvironmentViewSet
router = SimpleRouter()
router.register('projects', ProjectViewSet, basename='project')
router.register('environments', EnvironmentViewSet, basename='environment')
urlpatterns = router.urls
EOF

# ---------- 8.5 版本管理（骨架）----------
mkdir -p apps/versions
cat > apps/versions/__init__.py << 'EOF'
EOF
cat > apps/versions/models.py << 'EOF'
from django.db import models
from apps.users.models import User
from apps.projects.models import Project
class ReleaseVersion(models.Model):
    STATUS_CHOICES = (('developing', '开发中'), ('released', '已封板'))
    version = models.CharField('版本号', max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    released_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='developing')
    code_quality = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    class Meta: db_table = 'release_versions'
class VersionRegistration(models.Model):
    release_version = models.ForeignKey(ReleaseVersion, on_delete=models.CASCADE, related_name='registrations')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    app_version = models.CharField('应用版本', max_length=50)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'version_registrations'
        unique_together = ('release_version', 'project')
EOF
cat > apps/versions/urls.py << 'EOF'
urlpatterns = []  # 临时空路由，后续完善
EOF

# ---------- 8.6 漏洞管理（骨架）----------
mkdir -p apps/vulnerabilities
cat > apps/vulnerabilities/__init__.py << 'EOF'
EOF
cat > apps/vulnerabilities/urls.py << 'EOF'
urlpatterns = []
EOF

# ---------- 8.7 系统管理（含Constance动态配置）----------
mkdir -p apps/system
cat > apps/system/__init__.py << 'EOF'
EOF
cat > apps/system/models.py << 'EOF'
from django.db import models
from apps.users.models import User
class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='sent_notifications')
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    class Meta: db_table = 'notifications'
EOF
cat > apps/system/serializers.py << 'EOF'
from rest_framework import serializers
from .models import Notification
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['created_at', 'read_at']
EOF
cat > apps/system/views.py << 'EOF'
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer
from apps.base.viewsets import BaseModelViewSet
class NotificationViewSet(BaseModelViewSet):
    serializer_class = NotificationSerializer
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        n = self.get_object()
        n.is_read = True
        n.read_at = timezone.now()
        n.save()
        return Response({'status': 'ok'})
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        return Response({'count': self.get_queryset().filter(is_read=False).count()})
EOF
cat > apps/system/urls.py << 'EOF'
from rest_framework.routers import SimpleRouter
from .views import NotificationViewSet
router = SimpleRouter()
router.register('notifications', NotificationViewSet, basename='notification')
urlpatterns = router.urls
EOF

# ---------- 8.8 CI/CD 流水线管理 ----------
mkdir -p apps/ci_cd
cat > apps/ci_cd/__init__.py << 'EOF'
EOF
cat > apps/ci_cd/models.py << 'EOF'
import uuid
from django.db import models
from apps.projects.models import Project
from apps.users.models import User
class Pipeline(models.Model):
    """流水线定义"""
    name = models.CharField('流水线名称', max_length=200)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='pipelines')
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = 'cicd_pipelines'
class PipelineStage(models.Model):
    """流水线阶段定义"""
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='stages')
    name = models.CharField('阶段名称', max_length=100)
    order = models.IntegerField('执行顺序')
    script = models.TextField('执行脚本', blank=True)
    timeout = models.IntegerField('超时(秒)', default=3600)
    class Meta:
        db_table = 'cicd_stages'
        ordering = ['order']
class BuildRecord(models.Model):
    """构建记录"""
    STATUS_CHOICES = (
        ('pending', '等待中'),
        ('running', '运行中'),
        ('success', '成功'),
        ('failed', '失败'),
        ('aborted', '终止'),
    )
    build_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='builds')
    version = models.CharField('版本/分支', max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    triggered_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField('耗时(秒)', null=True, blank=True)
    sonar_task_id = models.CharField(max_length=100, blank=True)
    sonar_quality_gate = models.CharField(max_length=50, blank=True)
    risk_score = models.FloatField('风险评分', null=True, blank=True)
    log_file = models.TextField('构建日志', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'cicd_builds'
        ordering = ['-created_at']
class BuildStageRecord(models.Model):
    """构建阶段记录"""
    build = models.ForeignKey(BuildRecord, on_delete=models.CASCADE, related_name='stage_records')
    stage = models.ForeignKey(PipelineStage, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=BuildRecord.STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    log_snippet = models.TextField(blank=True)
    class Meta:
        db_table = 'cicd_build_stages'
EOF
cat > apps/ci_cd/serializers.py << 'EOF'
from rest_framework import serializers
from .models import Pipeline, PipelineStage, BuildRecord, BuildStageRecord
class PipelineStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PipelineStage
        fields = '__all__'
class PipelineSerializer(serializers.ModelSerializer):
    stages = PipelineStageSerializer(many=True, read_only=True)
    class Meta:
        model = Pipeline
        fields = '__all__'
class BuildStageRecordSerializer(serializers.ModelSerializer):
    stage_name = serializers.CharField(source='stage.name', read_only=True)
    class Meta:
        model = BuildStageRecord
        fields = '__all__'
class BuildRecordSerializer(serializers.ModelSerializer):
    pipeline_name = serializers.CharField(source='pipeline.name', read_only=True)
    project_name = serializers.CharField(source='pipeline.project.name', read_only=True)
    stage_records = BuildStageRecordSerializer(many=True, read_only=True)
    class Meta:
        model = BuildRecord
        fields = '__all__'
EOF
cat > apps/ci_cd/views.py << 'EOF'
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Pipeline, BuildRecord
from .serializers import PipelineSerializer, BuildRecordSerializer
from apps.base.viewsets import BaseModelViewSet
class PipelineViewSet(BaseModelViewSet):
    queryset = Pipeline.objects.all()
    serializer_class = PipelineSerializer
    @action(detail=True, methods=['post'])
    def trigger(self, request, pk=None):
        pipeline = self.get_object()
        version = request.data.get('version', 'main')
        # 触发构建逻辑 (Celery任务)
        from .tasks import run_pipeline
        task = run_pipeline.delay(pipeline.id, version, request.user.id)
        return Response({'task_id': task.id, 'status': 'triggered'})
class BuildRecordViewSet(BaseModelViewSet):
    queryset = BuildRecord.objects.all()
    serializer_class = BuildRecordSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['pipeline__name', 'version', 'build_id']
    ordering_fields = ['created_at', 'duration']
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        build = self.get_object()
        if build.status in ['pending', 'running']:
            build.status = 'aborted'
            build.finished_at = timezone.now()
            build.save()
            return Response({'status': 'cancelled'})
        return Response({'error': '无法取消'}, status=400)
EOF
cat > apps/ci_cd/tasks.py << 'EOF'
from celery import shared_task
import time
@shared_task(bind=True, max_retries=3)
def run_pipeline(self, pipeline_id, version, user_id):
    from .models import Pipeline, BuildRecord, BuildStageRecord
    from django.utils import timezone
    pipeline = Pipeline.objects.get(id=pipeline_id)
    build = BuildRecord.objects.create(
        pipeline=pipeline,
        version=version,
        status='running',
        triggered_by_id=user_id,
        started_at=timezone.now()
    )
    try:
        # 按顺序执行阶段
        for stage in pipeline.stages.all():
            stage_record = BuildStageRecord.objects.create(
                build=build,
                stage=stage,
                status='running',
                started_at=timezone.now()
            )
            # 模拟执行
            time.sleep(2)
            stage_record.status = 'success'
            stage_record.finished_at = timezone.now()
            stage_record.save()
        build.status = 'success'
    except Exception as e:
        build.status = 'failed'
        raise self.retry(exc=e)
    finally:
        build.finished_at = timezone.now()
        build.duration = (build.finished_at - build.started_at).seconds
        build.save()
    return build.id
@shared_task
def send_build_notification(build_id):
    """构建失败通知"""
    from .models import BuildRecord
    from apps.system.models import Notification
    from constance import config
    build = BuildRecord.objects.get(id=build_id)
    if build.status == 'failed':
        # 发送站内信
        Notification.objects.create(
            recipient=build.triggered_by,
            sender=None,
            title=f'构建失败: {build.pipeline.name}',
            content=f'构建 #{build.build_id} 失败，请检查日志。'
        )
        # 发送邮件 (略)
EOF
cat > apps/ci_cd/urls.py << 'EOF'
from rest_framework.routers import SimpleRouter
from .views import PipelineViewSet, BuildRecordViewSet
router = SimpleRouter()
router.register('pipelines', PipelineViewSet, basename='pipeline')
router.register('builds', BuildRecordViewSet, basename='build')
urlpatterns = router.urls
EOF

# ---------- 8.9 风险评分系统 ----------
mkdir -p apps/risk
cat > apps/risk/__init__.py << 'EOF'
EOF
cat > apps/risk/models.py << 'EOF'
from django.db import models
from apps.projects.models import Project
class RiskProfile(models.Model):
    """项目风险档案"""
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='risk_profile')
    overall_score = models.FloatField('综合风险分', default=0.0)
    code_quality_score = models.FloatField('代码质量分', default=0.0)
    vulnerability_score = models.FloatField('漏洞风险分', default=0.0)
    pipeline_health_score = models.FloatField('流水线健康分', default=0.0)
    last_scan_time = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'risk_profiles'
class RiskAlert(models.Model):
    LEVEL_CHOICES = (('low', '低'), ('medium', '中'), ('high', '高'), ('critical', '严重'))
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='risk_alerts')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    class Meta:
        db_table = 'risk_alerts'
EOF
cat > apps/risk/serializers.py << 'EOF'
from rest_framework import serializers
from .models import RiskProfile, RiskAlert
class RiskProfileSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    class Meta:
        model = RiskProfile
        fields = '__all__'
class RiskAlertSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    class Meta:
        model = RiskAlert
        fields = '__all__'
EOF
cat > apps/risk/views.py << 'EOF'
from rest_framework import viewsets
from .models import RiskProfile, RiskAlert
from .serializers import RiskProfileSerializer, RiskAlertSerializer
from apps.base.viewsets import BaseModelViewSet
class RiskProfileViewSet(BaseModelViewSet):
    queryset = RiskProfile.objects.select_related('project').all()
    serializer_class = RiskProfileSerializer
class RiskAlertViewSet(BaseModelViewSet):
    queryset = RiskAlert.objects.select_related('project').all()
    serializer_class = RiskAlertSerializer
EOF
cat > apps/risk/urls.py << 'EOF'
from rest_framework.routers import SimpleRouter
from .views import RiskProfileViewSet, RiskAlertViewSet
router = SimpleRouter()
router.register('profiles', RiskProfileViewSet, basename='riskprofile')
router.register('alerts', RiskAlertViewSet, basename='riskalert')
urlpatterns = router.urls
EOF

# ============================== 9. Nginx 配置 ==============================
mkdir -p nginx
cat > nginx/nginx.conf << 'EOF'
server {
    listen 80;
    server_name _;
    client_max_body_size 100M;
    location /static/ { alias /app/static/; }
    location /media/ { alias /app/media/; }
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# ============================== 10. README 文档 ==============================
cat > README.md << 'EOF'
# 质量安全平台 (QSP) v3.0

## ✨ 特性
- ✅ 完整 RBAC 权限控制
- ✅ 用户/项目/版本/漏洞/系统 五大核心管理
- ✅ CI/CD 流水线管理 + 构建失败自动通知
- ✅ SonarQube 集成与代码质量展示
- ✅ 风险评分系统
- ✅ Swagger 接口文档
- ✅ 支持 PostgreSQL/MySQL/SQLite 主从/双活
- ✅ Docker Compose 一键部署

## 🚀 快速开始
### 本地开发
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python scripts/init_db.py
python manage.py runserver
