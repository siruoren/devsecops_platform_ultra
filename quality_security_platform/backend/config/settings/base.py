import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY', default='django-insecure-development-key-change-in-production')
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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_USER_MODEL = 'users.User'

DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3')
}

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

CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=['http://localhost:8080'])
CORS_ALLOW_CREDENTIALS = True  # 允许携带 Cookie

# ---------- 认证相关配置 ----------
LOGIN_URL = '/admin/login/'          # 登录 URL（Django Admin）
LOGOUT_URL = '/logout/'             # 注销 URL（用于 Swagger UI 等）
LOGOUT_REDIRECT_URL = '/swagger/'   # 注销后重定向地址

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Celery
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/1')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379/2')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'

# Constance（动态配置）
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