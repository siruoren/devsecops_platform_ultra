from rest_framework.routers import SimpleRouter
from django.urls import path
from . import views
from .views import NotificationViewSet, AuditLogViewSet

router = SimpleRouter()
router.register('notifications', NotificationViewSet, basename='notification')
router.register('audit-logs', AuditLogViewSet, basename='audit-log')

urlpatterns = [
    # 上传企业图标
    path('upload-logo/', views.upload_company_logo, name='upload_company_logo'),
    # 保存网站设置
    path('save-site-settings/', views.save_site_settings, name='save_site_settings'),
    # 获取网站设置
    path('get-site-settings/', views.get_site_settings, name='get_site_settings'),
    # 重置企业图标
    path('reset-company-logo/', views.reset_company_logo, name='reset_company_logo'),
    # 发送邮件通知
    path('send-email-notification/', views.send_email_notification, name='send_email_notification'),
    # 获取用户通知
    path('notifications/', views.get_user_notifications, name='get_user_notifications'),
    # 标记通知为已读
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    # 标记所有通知为已读
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    # 删除通知
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
]

urlpatterns += router.urls
