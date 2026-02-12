from rest_framework import serializers
from .models import SystemConfig, Notification
class SystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        exclude = ['id']
        read_only_fields = ['updated_at']
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['created_at', 'read_at']
