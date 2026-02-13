from .base import *
DEBUG = False
DATABASES = {
    'default': {
        'ENGINE': f'django.db.backends.{env("DB_ENGINE")}',
        'NAME': env('DB_NAME'), 'USER': env('DB_USER'), 'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'), 'PORT': env('DB_PORT'), 'CONN_MAX_AGE': 60,
    }
}
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
