import uuid
from django.db import models
from apps.projects.models import Project
from apps.users.models import User
class Pipeline(models.Model):
    """流水线定义"""
    name = models.CharField('流水线名称', max_length=200)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='pipelines')
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = 'cicd_pipelines'
class PipelineStage(models.Model):
    """流水线阶段定义"""
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='stages')
    name = models.CharField('阶段名称', max_length=100)
    order = models.IntegerField('执行顺序')
    script = models.TextField('执行脚本', blank=True)
    timeout = models.IntegerField('超时(秒)', default=3600)
    class Meta:
        db_table = 'cicd_stages'
        ordering = ['order']
class BuildRecord(models.Model):
    """构建记录"""
    STATUS_CHOICES = (
        ('pending', '等待中'),
        ('running', '运行中'),
        ('success', '成功'),
        ('failed', '失败'),
        ('aborted', '终止'),
    )
    build_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='builds')
    version = models.CharField('版本/分支', max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    triggered_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField('耗时(秒)', null=True, blank=True)
    sonar_task_id = models.CharField(max_length=100, blank=True)
    sonar_quality_gate = models.CharField(max_length=50, blank=True)
    risk_score = models.FloatField('风险评分', null=True, blank=True)
    log_file = models.TextField('构建日志', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'cicd_builds'
        ordering = ['-created_at']
class BuildStageRecord(models.Model):
    """构建阶段记录"""
    build = models.ForeignKey(BuildRecord, on_delete=models.CASCADE, related_name='stage_records')
    stage = models.ForeignKey(PipelineStage, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=BuildRecord.STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    log_snippet = models.TextField(blank=True)
    class Meta:
        db_table = 'cicd_build_stages'
