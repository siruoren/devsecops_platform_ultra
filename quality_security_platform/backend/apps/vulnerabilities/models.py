from django.db import models
from apps.projects.models import Project

class DependencyCheckScan(models.Model):
    """
    Dependency-Check 扫描记录
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='dependency_scans')
    scan_date = models.DateTimeField('扫描日期', auto_now_add=True)
    file_name = models.CharField('文件名', max_length=255)
    file_size = models.IntegerField('文件大小', default=0)
    total_vulnerabilities = models.IntegerField('总漏洞数', default=0)
    class Meta: db_table = 'vulnerabilities_dependency_check_scans'
    def __str__(self):
        return f'{self.project.name} - {self.scan_date}'

class ArtifactVulnerability(models.Model):
    """
    工件漏洞记录
    """
    SEVERITY_CHOICES = (
        ('critical', '严重'),
        ('high', '高危'),
        ('medium', '中危'),
        ('low', '低危'),
        ('info', '信息')
    )
    scan = models.ForeignKey(DependencyCheckScan, on_delete=models.CASCADE, related_name='vulnerabilities')
    artifact_name = models.CharField('工件名称', max_length=255)
    artifact_version = models.CharField('工件版本', max_length=100)
    cve = models.CharField('CVE编号', max_length=50, blank=True)
    severity = models.CharField('严重性', max_length=20, choices=SEVERITY_CHOICES, default='medium')
    cvss_score = models.FloatField('CVSS评分', null=True, blank=True)
    description = models.TextField('漏洞描述', blank=True)
    recommendation = models.TextField('修复建议', blank=True)
    class Meta: db_table = 'vulnerabilities_artifact_vulnerabilities'
    def __str__(self):
        return f'{self.artifact_name} {self.artifact_version} - {self.cve}'

class ArtifactVersionChange(models.Model):
    """
    工件版本变更记录
    """
    NOTIFICATION_CHOICES = (
        ('in_app', '站内信'),
        ('email', '邮件'),
        ('both', '两者')
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='artifact_changes')
    artifact_group = models.CharField('工件组织', max_length=255)
    artifact_name = models.CharField('工件名称', max_length=255)
    old_version = models.CharField('旧版本', max_length=100)
    new_version = models.CharField('新版本', max_length=100)
    change_date = models.DateTimeField('变更日期', auto_now_add=True)
    notification_type = models.CharField('通知方式', max_length=20, choices=NOTIFICATION_CHOICES, default='in_app')
    is_notified = models.BooleanField('是否已通知', default=False)
    class Meta: db_table = 'vulnerabilities_artifact_version_changes'
    def __str__(self):
        return f'{self.artifact_name} {self.old_version} → {self.new_version}'