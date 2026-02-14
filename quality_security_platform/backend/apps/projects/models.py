from django.db import models
from apps.users.models import User
class Environment(models.Model):
    name = models.CharField('环境名', max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: db_table = 'environments'
    def __str__(self):
        return self.name
class ServerIP(models.Model):
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE, related_name='server_ips')
    ip = models.CharField('IP地址', max_length=50)
    class Meta: db_table = 'server_ips'
    def __str__(self):
        return self.ip
class Project(models.Model):
    name = models.CharField('应用名', max_length=200, unique=True)
    git_repo = models.URLField('Git仓库地址')
    git_path = models.CharField('仓库内路径', max_length=500, default='/')
    environment = models.ForeignKey(Environment, on_delete=models.PROTECT)
    deploy_dir = models.CharField('部署目录', max_length=500)
    start_script = models.CharField('启动脚本', max_length=500)
    stop_script = models.CharField('停止脚本', max_length=500)
    start_cron = models.CharField('启动Cron', max_length=100, blank=True)
    stop_cron = models.CharField('停止Cron', max_length=100, blank=True)
    sonarqube_url = models.URLField('SonarQube项目地址', blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: db_table = 'projects'
    def __str__(self):
        return self.name
