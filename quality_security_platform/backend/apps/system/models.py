from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class Notification(models.Model):
    """
    站内通知
    """
    TYPE_CHOICES = (
        ('system', '系统通知'),
        ('vulnerability', '漏洞通知'),
        ('pipeline', '流水线通知'),
        ('artifact', '工件通知')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    notification_type = models.CharField('通知类型', max_length=20, choices=TYPE_CHOICES, default='system')
    is_read = models.BooleanField('是否已读', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    class Meta: db_table = 'system_notifications'
    def __str__(self):
        return f'{self.user.username} - {self.title}'

class SystemConfig(models.Model):
    """
    系统配置
    """
    key = models.CharField('配置键', max_length=100, unique=True)
    value = models.TextField('配置值')
    description = models.CharField('描述', max_length=255, blank=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    class Meta: db_table = 'system_configs'
    def __str__(self):
        return self.key
