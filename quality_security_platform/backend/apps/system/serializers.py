from rest_framework import serializers
from .models import Notification, SystemConfig, AuditLog
from apps.users.serializers import UserSerializer

class NotificationSerializer(serializers.ModelSerializer):
    """通知序列化器"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = ('id', 'user', 'title', 'content', 'notification_type', 'is_read', 'created_at')

class SystemConfigSerializer(serializers.ModelSerializer):
    """系统配置序列化器"""
    class Meta:
        model = SystemConfig
        fields = ('key', 'value', 'description', 'updated_at')

class AuditLogSerializer(serializers.ModelSerializer):
    """审计日志序列化器"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AuditLog
        fields = ('id', 'user', 'action', 'resource_type', 'resource_id', 'description', 'ip_address', 'user_agent', 'created_at')
