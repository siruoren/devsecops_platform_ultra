from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
class SystemConfig(models.Model):
    web_port = models.IntegerField(default=8000)
    max_daily_messages = models.IntegerField(default=100, validators=[MinValueValidator(1)])
    smtp_server = models.CharField(max_length=255)
    smtp_port = models.IntegerField(default=587)
    smtp_username = models.CharField(max_length=255)
    smtp_password = models.CharField(max_length=255)
    sender_email = models.EmailField()
    sender_name = models.CharField(max_length=100, default='质量安全平台')
    max_daily_emails = models.IntegerField(default=500, validators=[MinValueValidator(1)])
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('users.User', null=True, on_delete=models.SET_NULL)
    class Meta: db_table = 'system_config'
    @classmethod
    def get_config(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
class Notification(models.Model):
    recipient = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey('users.User', null=True, on_delete=models.SET_NULL, related_name='sent_notifications')
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    class Meta: db_table = 'notifications'
