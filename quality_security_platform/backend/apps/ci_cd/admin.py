from django.contrib import admin
from .models import Pipeline, PipelineStage, BuildRecord, BuildStageRecord, JenkinsCredential, JenkinsJob, JenkinsBuild, JenkinsBuildParameter

from django.urls import reverse
from django.utils.html import format_html

@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'created_by', 'created_at', 'is_active', 'pipeline_actions')
    list_filter = ('project', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    
    def pipeline_actions(self, obj):
        """添加操作按钮"""
        config_url = reverse('admin:ci_cd_pipeline_change', args=[obj.id])
        start_url = f'/api/cicd/start-build/{obj.id}/'
        cancel_url = f'/api/cicd/cancel-build/{obj.id}/'
        return format_html(
            '<a href="{0}" class="btn btn-sm btn-primary mr-1">修改配置</a> '
            '<a href="{1}" class="btn btn-sm btn-success mr-1">开始构建</a> '
            '<a href="{2}" class="btn btn-sm btn-danger">取消构建</a>',
            config_url, start_url, cancel_url
        )
    pipeline_actions.short_description = '操作'
    
    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(PipelineStage)
class PipelineStageAdmin(admin.ModelAdmin):
    list_display = ('pipeline', 'name', 'order', 'timeout')
    list_filter = ('pipeline',)
    search_fields = ('name',)

@admin.register(BuildRecord)
class BuildRecordAdmin(admin.ModelAdmin):
    list_display = ('build_id', 'pipeline', 'version', 'status', 'triggered_by', 'created_at', 'duration')
    list_filter = ('pipeline', 'status', 'created_at')
    search_fields = ('build_id', 'version')
    raw_id_fields = ('triggered_by',)
    exclude = ('started_at', 'finished_at')

@admin.register(BuildStageRecord)
class BuildStageRecordAdmin(admin.ModelAdmin):
    list_display = ('build', 'stage', 'status', 'started_at', 'finished_at')
    list_filter = ('status',)
    exclude = ('started_at', 'finished_at')

@admin.register(JenkinsCredential)
class JenkinsCredentialAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'username', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'url', 'username')
    
    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(JenkinsJob)
class JenkinsJobAdmin(admin.ModelAdmin):
    list_display = ('name', 'credential', 'jenkins_url', 'pipeline', 'is_active', 'created_by', 'created_at')
    list_filter = ('credential', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'jenkins_url')
    raw_id_fields = ('created_by',)
    
    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(JenkinsBuild)
class JenkinsBuildAdmin(admin.ModelAdmin):
    list_display = ('jenkins_job', 'jenkins_build_number', 'status', 'triggered_by', 'started_at', 'finished_at', 'duration')
    list_filter = ('jenkins_job', 'status', 'created_at')
    search_fields = ('jenkins_build_url', 'parameters')
    raw_id_fields = ('triggered_by',)
    exclude = ('started_at', 'finished_at')

@admin.register(JenkinsBuildParameter)
class JenkinsBuildParameterAdmin(admin.ModelAdmin):
    list_display = ('jenkins_job', 'name', 'display_name', 'parameter_type', 'is_required')
    list_filter = ('jenkins_job', 'parameter_type', 'is_required')
    search_fields = ('name', 'display_name')
