from rest_framework import serializers
from .models import Project, Environment
class EnvironmentSerializer(serializers.ModelSerializer):
    class Meta: model = Environment; fields = '__all__'
class ProjectSerializer(serializers.ModelSerializer):
    environment_name = serializers.CharField(source='environment.name', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    class Meta: model = Project; fields = '__all__'
