from django.db import models
from apps.projects.models import Project
class RiskProfile(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='risk_profile')
    overall_score = models.FloatField('综合风险分', default=0.0)
    code_quality_score = models.FloatField('代码质量分', default=0.0)
    vulnerability_score = models.FloatField('漏洞风险分', default=0.0)
    pipeline_health_score = models.FloatField('流水线健康分', default=0.0)
    last_scan_time = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: db_table = 'risk_profiles'
class RiskAlert(models.Model):
    LEVEL_CHOICES = (('low','低'),('medium','中'),('high','高'),('critical','严重'))
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='risk_alerts')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    class Meta: db_table = 'risk_alerts'
