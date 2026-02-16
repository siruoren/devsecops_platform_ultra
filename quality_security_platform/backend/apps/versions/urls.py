from django.urls import path
from . import views

urlpatterns = [
    # 获取所有发布版本
    path('', views.get_versions, name='get_versions'),
    # 获取版本详情
    path('<int:version_id>/', views.get_version_detail, name='get_version_detail'),
    # 创建发布版本
    path('create/', views.create_version, name='create_version'),
    # 更新发布版本
    path('<int:version_id>/update/', views.update_version, name='update_version'),
    # 删除发布版本
    path('<int:version_id>/delete/', views.delete_version, name='delete_version'),
    # 创建版本登记
    path('registration/create/', views.create_version_registration, name='create_version_registration'),
    # 更新版本登记
    path('registration/<int:registration_id>/update/', views.update_version_registration, name='update_version_registration'),
    # 删除版本登记
    path('registration/<int:registration_id>/delete/', views.delete_version_registration, name='delete_version_registration'),
]
