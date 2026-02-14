from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('users/', views.users, name='users'),
    path('projects/', views.projects, name='projects'),
    path('versions/', views.versions, name='versions'),
    path('vulnerability/', views.vulnerability, name='vulnerability'),
    path('cicd/', views.cicd, name='cicd'),
    path('risk/', views.risk, name='risk'),
    path('system/', views.system, name='system'),
]