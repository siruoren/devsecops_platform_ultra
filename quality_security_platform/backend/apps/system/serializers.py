from rest_framework import serializers
from .models import Notification
from apps.users.serializers import UserSerializer

class NotificationSerializer(serializers.ModelSerializer):
    """通知序列化器"""
    recipient = UserSerializer(read_only=True)
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = ('id', 'recipient', 'sender', 'title', 'content', 'is_read', 'created_at', 'read_at')
