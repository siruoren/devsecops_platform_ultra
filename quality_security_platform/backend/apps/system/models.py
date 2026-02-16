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

class AuditLog(models.Model):
    """
    审计日志
    """
    ACTION_CHOICES = (
        ('login', '登录'),
        ('logout', '登出'),
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('upload', '上传'),
        ('download', '下载'),
        ('execute', '执行'),
        ('other', '其他')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField('操作类型', max_length=20, choices=ACTION_CHOICES, default='other')
    resource_type = models.CharField('资源类型', max_length=100, blank=True)
    resource_id = models.CharField('资源ID', max_length=100, blank=True)
    description = models.TextField('操作描述', blank=True)
    ip_address = models.CharField('IP地址', max_length=50, blank=True)
    user_agent = models.CharField('用户代理', max_length=500, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    class Meta: db_table = 'system_audit_logs'
    def __str__(self):
        return f'{self.user.username} - {self.action} - {self.created_at}'
