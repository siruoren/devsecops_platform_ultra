import uuid
from django.db import models
from apps.projects.models import Project
from apps.users.models import User
class Pipeline(models.Model):
    name = models.CharField('流水线名称', max_length=200)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='pipelines')
    description = models.TextField(blank=True)
    pipeline_url = models.URLField('流水线URL', max_length=500, blank=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    class Meta: db_table = 'cicd_pipelines'
    def __str__(self):
        return self.name
class PipelineStage(models.Model):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='stages')
    name = models.CharField('阶段名称', max_length=100)
    order = models.IntegerField('执行顺序')
    script = models.TextField('执行脚本', blank=True)
    timeout = models.IntegerField('超时(秒)', default=3600)
    class Meta: db_table = 'cicd_stages'; ordering = ['order']
class BuildRecord(models.Model):
    STATUS_CHOICES = (('pending','等待中'),('running','运行中'),('success','成功'),('failed','失败'),('aborted','终止'))
    build_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='builds')
    version = models.CharField('版本/分支', max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    triggered_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    sonar_task_id = models.CharField(max_length=100, blank=True)
    sonar_quality_gate = models.CharField(max_length=50, blank=True)
    risk_score = models.FloatField(null=True, blank=True)
    log_file = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: db_table = 'cicd_builds'; ordering = ['-created_at']
class BuildStageRecord(models.Model):
    build = models.ForeignKey(BuildRecord, on_delete=models.CASCADE, related_name='stage_records')
    stage = models.ForeignKey(PipelineStage, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=BuildRecord.STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    log_snippet = models.TextField(blank=True)
    class Meta: db_table = 'cicd_build_stages'
class JenkinsCredential(models.Model):
    name = models.CharField('凭证名称', max_length=100, unique=True)
    url = models.URLField('Jenkins URL', max_length=500)
    username = models.CharField('用户名', max_length=100)
    password = models.CharField('密码', max_length=200)
    description = models.TextField('描述', blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: db_table = 'cicd_jenkins_credentials'
    def __str__(self):
        return self.name

class JenkinsJob(models.Model):
    name = models.CharField('任务名称', max_length=200, unique=True)
    description = models.TextField('描述', blank=True)
    jenkins_url = models.URLField('Jenkins任务URL', max_length=500)
    credential = models.ForeignKey(JenkinsCredential, on_delete=models.CASCADE, related_name='jobs')
    pipeline = models.ForeignKey(Pipeline, null=True, blank=True, on_delete=models.SET_NULL, related_name='jenkins_jobs')
    parameters = models.JSONField('任务参数', blank=True, default=dict)
    is_active = models.BooleanField('是否启用', default=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: db_table = 'cicd_jenkins_jobs'
    def __str__(self):
        return self.name

class JenkinsBuild(models.Model):
    STATUS_CHOICES = (('pending','等待中'),('running','运行中'),('success','成功'),('failed','失败'),('aborted','终止'))
    build_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    jenkins_job = models.ForeignKey(JenkinsJob, on_delete=models.CASCADE, related_name='builds')
    jenkins_build_number = models.IntegerField('Jenkins构建编号', null=True, blank=True)
    jenkins_build_url = models.URLField('Jenkins构建URL', max_length=500, blank=True)
    parameters = models.JSONField('构建参数', blank=True, default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    log = models.TextField('构建日志', blank=True)
    triggered_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField('构建时长(秒)', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: db_table = 'cicd_jenkins_builds'; ordering = ['-created_at']
    def __str__(self):
        return f'{self.jenkins_job.name} #{self.jenkins_build_number or self.build_id}'

class JenkinsBuildParameter(models.Model):
    jenkins_job = models.ForeignKey(JenkinsJob, on_delete=models.CASCADE, related_name='build_parameters')
    name = models.CharField('参数名称', max_length=100)
    display_name = models.CharField('显示名称', max_length=200, blank=True)
    parameter_type = models.CharField('参数类型', max_length=50)  # string, choice, boolean, etc.
    default_value = models.CharField('默认值', max_length=500, blank=True)
    choices = models.JSONField('可选值', blank=True, default=list)
    description = models.TextField('描述', blank=True)
    is_required = models.BooleanField('是否必填', default=True)
    class Meta: db_table = 'cicd_jenkins_build_parameters'
    def __str__(self):
        return f'{self.jenkins_job.name}: {self.name} ({self.parameter_type})'
