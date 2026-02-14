from django.contrib import admin
from .models import Pipeline, PipelineStage, BuildRecord, BuildStageRecord


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'project', 'pipeline_url', 'created_by', 'is_active', 'created_at')
    search_fields = ('name', 'project__name', 'description', 'pipeline_url')
    list_filter = ('project', 'is_active', 'created_by')
    ordering = ('-created_at',)
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PipelineStage)
class PipelineStageAdmin(admin.ModelAdmin):
    list_display = ('id', 'pipeline', 'name', 'order', 'timeout')
    search_fields = ('pipeline__name', 'name')
    list_filter = ('pipeline',)
    ordering = ('pipeline', 'order')


@admin.register(BuildRecord)
class BuildRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'build_id', 'pipeline', 'version', 'status', 'triggered_by', 'started_at', 'finished_at', 'duration', 'created_at')
    search_fields = ('build_id', 'pipeline__name', 'version', 'status')
    list_filter = ('pipeline', 'status', 'triggered_by')
    ordering = ('-created_at',)
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.triggered_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(BuildStageRecord)
class BuildStageRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'build', 'stage', 'status', 'started_at', 'finished_at')
    search_fields = ('build__build_id', 'stage__name', 'status')
    list_filter = ('build__pipeline', 'stage', 'status')
    ordering = ('build', 'stage__order')
