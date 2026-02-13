from rest_framework import serializers
from .models import RiskProfile, RiskAlert
class RiskProfileSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    class Meta: model = RiskProfile; fields = '__all__'
class RiskAlertSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    class Meta: model = RiskAlert; fields = '__all__'
