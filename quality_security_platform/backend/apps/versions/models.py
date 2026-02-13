from django.db import models
from apps.users.models import User
from apps.projects.models import Project
class ReleaseVersion(models.Model):
    STATUS_CHOICES = (('developing', '开发中'), ('released', '已封板'))
    version = models.CharField('版本号', max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    released_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='developing')
    code_quality = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    class Meta: db_table = 'release_versions'
class VersionRegistration(models.Model):
    release_version = models.ForeignKey(ReleaseVersion, on_delete=models.CASCADE, related_name='registrations')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    app_version = models.CharField('应用版本', max_length=50)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: db_table = 'version_registrations'
