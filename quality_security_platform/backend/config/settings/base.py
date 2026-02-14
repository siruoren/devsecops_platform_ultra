import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY', default='django-insecure-development-key-change-in-production')
DEBUG = env.bool('DEBUG', False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

INSTALLED_APPS = [
    'simpleui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 第三方
    'rest_framework',
    'corsheaders',
    # 'django-filter',
    'drf_yasg',
    'constance',
    'constance.backends.database',
    # 本地应用
    'web',
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
    # 动态更新Admin站点设置的中间件
    'config.middleware.dynamic_admin_settings.DynamicAdminSettingsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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
        # 'django_filters.rest_framework.DjangoFilterBackend',
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
LOGOUT_REDIRECT_URL = '/admin/login/'   # 注销后重定向地址

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
    # 网站标题设置
    'SITE_HEADER': ('质量安全平台', '登录页面标题'),
    'SITE_TITLE': ('质量安全平台', '浏览器标签标题'),
    'INDEX_TITLE': ('系统管理', '首页标题'),
    # 企业图标
    'COMPANY_LOGO': ('', '企业图标路径'),
}

# SimpleUI 配置
# 注意：SIMPLEUI_LOGO 需要在 Django 应用加载后设置
# 我们将在 urls.py 中处理这个问题

SIMPLEUI_CONFIG = {
    'system_keep': True,
    'menu_display': ['用户与权限', '项目管理', '版本管理', 'CI/CD管理', '风险管理', '系统管理', '其他'],
    'menus': [
        {
            'name': '用户与权限',
            'icon': 'fas fa-users-cog',
            'models': [
                {
                    'name': '用户管理',
                    'url': '/admin/users/user/',
                    'icon': 'fas fa-user'
                },
                {
                    'name': '角色管理',
                    'url': '/admin/rbac/role/',
                    'icon': 'fas fa-user-tag'
                },
                {
                    'name': '权限管理',
                    'url': '/admin/rbac/permission/',
                    'icon': 'fas fa-lock'
                },
                {
                    'name': '用户角色分配',
                    'url': '/admin/rbac/userrole/',
                    'icon': 'fas fa-user-plus'
                }
            ]
        },
        {
            'name': '项目管理',
            'icon': 'fas fa-project-diagram',
            'models': [
                {
                    'name': '项目管理',
                    'url': '/admin/projects/project/',
                    'icon': 'fas fa-project-diagram'
                },
                {
                    'name': '环境管理',
                    'url': '/admin/projects/environment/',
                    'icon': 'fas fa-server'
                }
            ]
        },
        {
            'name': '版本管理',
            'icon': 'fas fa-code-branch',
            'models': [
                {
                    'name': '发布版本',
                    'url': '/admin/versions/releaseversion/',
                    'icon': 'fas fa-code-branch'
                },
                {
                    'name': '版本登记',
                    'url': '/admin/versions/versionregistration/',
                    'icon': 'fas fa-clipboard-list'
                }
            ]
        },
        {
            'name': 'CI/CD管理',
            'icon': 'fas fa-cogs',
            'models': [
                {
                    'name': '流水线管理',
                    'url': '/admin/ci_cd/pipeline/',
                    'icon': 'fas fa-cogs'
                },
                {
                    'name': '流水线阶段',
                    'url': '/admin/ci_cd/pipelinestage/',
                    'icon': 'fas fa-layer-group'
                },
                {
                    'name': '构建记录',
                    'url': '/admin/ci_cd/buildrecord/',
                    'icon': 'fas fa-history'
                },
                {
                    'name': '构建阶段记录',
                    'url': '/admin/ci_cd/buildstagerecord/',
                    'icon': 'fas fa-tasks'
                }
            ]
        },
        {
            'name': '风险管理',
            'icon': 'fas fa-exclamation-triangle',
            'models': [
                {
                    'name': '风险档案',
                    'url': '/admin/risk/riskprofile/',
                    'icon': 'fas fa-file-alt'
                },
                {
                    'name': '风险告警',
                    'url': '/admin/risk/riskalert/',
                    'icon': 'fas fa-bell'
                }
            ]
        },
        {
            'name': '系统管理',
            'icon': 'fas fa-cog',
            'models': [
                {
                    'name': '通知管理',
                    'url': '/admin/system/notification/',
                    'icon': 'fas fa-bell'
                },
                {
                    'name': '动态配置',
                    'url': '/admin/constance/config/',
                    'icon': 'fas fa-sliders-h'
                },
                {
                    'name': '网站设置',
                    'url': '/logo-upload/',
                    'icon': 'fas fa-image'
                }
            ]
        },
        {
            'name': '其他',
            'icon': 'fas fa-ellipsis-h',
            'models': [
                {
                    'name': 'API文档',
                    'url': '/api/docs/',
                    'icon': 'fas fa-book'
                },
                {
                    'name': 'Swagger UI',
                    'url': '/swagger/',
                    'icon': 'fas fa-swagger'
                },
                {
                    'name': 'ReDoc',
                    'url': '/redoc/',
                    'icon': 'fas fa-file-alt'
                }
            ]
        }
    ]
}

# SimpleUI 主题设置
SIMPLEUI_DEFAULT_THEME = 'admin.lte.css'
# 默认不使用自定义 logo
SIMPLEUI_LOGO = None
SIMPLEUI_HOME_INFO = False
SIMPLEUI_ANALYSIS = False

# ========== 认证后端配置 ==========
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # 本地认证（始终保留）
]


# 统一认证后端（动态添加）
def get_auth_backends():
    """根据配置动态添加认证后端"""
    from apps.auth_unified.models import UnifiedAuthConfig

    try:
        config = UnifiedAuthConfig.get_config()
        backends = AUTHENTICATION_BACKENDS.copy()

        if config.enabled:
            if config.auth_type == 'ldap':
                backends.append('apps.auth_unified.backends.ldap.LDAPBackend')
            elif config.auth_type == 'keycloak':
                backends.append('apps.auth_unified.backends.oidc.OIDCAuthenticationBackend')
            elif config.auth_type == 'cas':
                backends.append('apps.auth_unified.backends.cas.CASBackend')

        return backends
    except Exception:
        return AUTHENTICATION_BACKENDS


# 由于无法在启动时动态执行数据库查询，可以在 settings 中保持静态配置
# 实际认证后端的选择通过中间件或自定义认证类实现
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    # 'apps.auth_unified.backends.ldap.LDAPBackend',  # 始终加载，内部会检查配置
    # 'apps.auth_unified.backends.oidc.OIDCAuthenticationBackend',  # 始终加载
    # 'apps.auth_unified.backends.cas.CASBackend',  # 始终加载
]

# ========== 添加统一认证应用 ==========
INSTALLED_APPS += [
    'apps.auth_unified',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'