from rest_framework import serializers
from .models import Pipeline, PipelineStage, BuildRecord, BuildStageRecord
class PipelineStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PipelineStage
        fields = '__all__'
class PipelineSerializer(serializers.ModelSerializer):
    stages = PipelineStageSerializer(many=True, read_only=True)
    class Meta:
        model = Pipeline
        fields = '__all__'
class BuildStageRecordSerializer(serializers.ModelSerializer):
    stage_name = serializers.CharField(source='stage.name', read_only=True)
    class Meta:
        model = BuildStageRecord
        fields = '__all__'
class BuildRecordSerializer(serializers.ModelSerializer):
    pipeline_name = serializers.CharField(source='pipeline.name', read_only=True)
    project_name = serializers.CharField(source='pipeline.project.name', read_only=True)
    stage_records = BuildStageRecordSerializer(many=True, read_only=True)
    class Meta:
        model = BuildRecord
        fields = '__all__'
