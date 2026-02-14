from rest_framework.routers import SimpleRouter
from django.urls import path
from . import views
from .views import NotificationViewSet

router = SimpleRouter()
router.register('notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('upload-logo/', views.upload_company_logo, name='upload_company_logo'),
]

urlpatterns += router.urls
