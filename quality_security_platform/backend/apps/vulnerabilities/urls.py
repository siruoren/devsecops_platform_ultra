from django.urls import path
from . import views

urlpatterns = [
    # 导入 Dependency-Check 扫描结果
    path('import-dependency-check/', views.import_dependency_check, name='import_dependency_check'),
    # 获取工件漏洞列表
    path('artifactvulnerabilities/', views.get_artifact_vulnerabilities, name='get_artifact_vulnerabilities'),
    # 创建工件版本变更记录
    path('artifact-version-change/', views.create_artifact_version_change, name='create_artifact_version_change'),
    # 获取项目漏洞统计
    path('vulnerability-stats/', views.get_project_vulnerability_stats, name='get_project_vulnerability_stats'),
]
