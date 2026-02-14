from django.urls import path
from . import views

app_name = 'auth_unified'

urlpatterns = [
    path('status/', views.auth_status, name='status'),
    path('oidc/login/', views.oidc_login, name='oidc_login'),
    path('oidc/callback/', views.oidc_callback, name='oidc_callback'),
]