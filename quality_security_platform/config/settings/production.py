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
