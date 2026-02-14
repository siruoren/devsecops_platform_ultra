from django.contrib import admin
from .models import RiskProfile, RiskAlert

@admin.register(RiskProfile)
class RiskProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'overall_score', 'code_quality_score', 'vulnerability_score', 'pipeline_health_score', 'last_scan_time', 'updated_at')
    search_fields = ('project__name',)
    list_filter = ('project',)
    ordering = ('-updated_at',)


@admin.register(RiskAlert)
class RiskAlertAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'level', 'title', 'is_resolved', 'created_at')
    search_fields = ('project__name', 'title', 'description')
    list_filter = ('project', 'level', 'is_resolved')
    ordering = ('-created_at',)
