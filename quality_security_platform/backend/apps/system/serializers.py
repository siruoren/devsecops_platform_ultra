from rest_framework import serializers
from .models import Notification, SystemConfig
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
