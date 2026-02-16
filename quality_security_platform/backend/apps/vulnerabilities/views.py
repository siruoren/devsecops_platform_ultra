from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import xml.etree.ElementTree as ET
from .models import DependencyCheckScan, ArtifactVulnerability, ArtifactVersionChange
from apps.projects.models import Project
import tempfile
import os
from django.db.models import Q

@csrf_exempt
def import_dependency_check(request):
    """
    导入 Dependency-Check 扫描结果
    """
    if request.method == 'POST':
        try:
            # 获取请求数据
            project_id = request.POST.get('project_id')
            file = request.FILES.get('file')
            
            # 验证参数
            if not project_id or not file:
                return JsonResponse({'status': 'error', 'message': '缺少必要参数'})
            
            # 获取项目
            project = Project.objects.get(id=project_id)
            
            # 保存上传的文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as temp_file:
                for chunk in file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            # 解析 XML 文件
            vulnerabilities = []
            total_vulnerabilities = 0
            
            try:
                tree = ET.parse(temp_file_path)
                root = tree.getroot()
                
                # 遍历漏洞记录
                for dependency in root.findall('.//{https://owasp.org/www-community/vulnerabilities}dependency'):
                    artifact_name = dependency.find('{https://owasp.org/www-community/vulnerabilities}name').text if dependency.find('{https://owasp.org/www-community/vulnerabilities}name') else ''
                    artifact_version = dependency.find('{https://owasp.org/www-community/vulnerabilities}version').text if dependency.find('{https://owasp.org/www-community/vulnerabilities}version') else ''
                    
                    # 查找漏洞
                    for vulnerability in dependency.findall('.//{https://owasp.org/www-community/vulnerabilities}vulnerability'):
                        cve = vulnerability.find('{https://owasp.org/www-community/vulnerabilities}name').text if vulnerability.find('{https://owasp.org/www-community/vulnerabilities}name') else ''
                        severity = vulnerability.find('{https://owasp.org/www-community/vulnerabilities}severity').text if vulnerability.find('{https://owasp.org/www-community/vulnerabilities}severity') else 'medium'
                        description = vulnerability.find('{https://owasp.org/www-community/vulnerabilities}description').text if vulnerability.find('{https://owasp.org/www-community/vulnerabilities}description') else ''
                        
                        # 映射严重性级别
                        severity_map = {
                            'CRITICAL': 'critical',
                            'HIGH': 'high',
                            'MEDIUM': 'medium',
                            'LOW': 'low',
                            'INFORMATIONAL': 'info'
                        }
                        mapped_severity = severity_map.get(severity.upper(), 'medium')
                        
                        vulnerabilities.append({
                            'artifact_name': artifact_name,
                            'artifact_version': artifact_version,
                            'cve': cve,
                            'severity': mapped_severity,
                            'description': description
                        })
                        total_vulnerabilities += 1
            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
            
            # 创建扫描记录
            scan = DependencyCheckScan.objects.create(
                project=project,
                file_name=file.name,
                file_size=file.size,
                total_vulnerabilities=total_vulnerabilities
            )
            
            # 创建漏洞记录
            for vuln_data in vulnerabilities:
                ArtifactVulnerability.objects.create(
                    scan=scan,
                    artifact_name=vuln_data['artifact_name'],
                    artifact_version=vuln_data['artifact_version'],
                    cve=vuln_data['cve'],
                    severity=vuln_data['severity'],
                    description=vuln_data['description']
                )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Dependency-Check 报告导入成功',
                'scan_id': scan.id,
                'total_vulnerabilities': total_vulnerabilities
            })
        except Exception as e:
            print(f"导入 Dependency-Check 报告失败: {e}")
            return JsonResponse({'status': 'error', 'message': '导入 Dependency-Check 报告失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

def get_artifact_vulnerabilities(request):
    """
    获取工件漏洞列表
    """
    if request.method == 'GET':
        try:
            # 获取过滤参数
            project_id = request.GET.get('project_id')
            search = request.GET.get('search')
            severity = request.GET.get('severity')
            
            # 构建查询
            queryset = ArtifactVulnerability.objects.all().order_by('-scan__scan_date')
            
            # 应用过滤
            if project_id:
                queryset = queryset.filter(scan__project_id=project_id)
            if search:
                queryset = queryset.filter(
                    Q(artifact_name__icontains=search) |
                    Q(artifact_version__icontains=search) |
                    Q(cve__icontains=search)
                )
            if severity:
                queryset = queryset.filter(severity=severity)
            
            # 构建响应数据
            vulnerabilities = []
            for vuln in queryset:
                vulnerabilities.append({
                    'id': vuln.id,
                    'artifact_name': vuln.artifact_name,
                    'artifact_version': vuln.artifact_version,
                    'cve': vuln.cve,
                    'severity': vuln.severity,
                    'cvss_score': vuln.cvss_score,
                    'description': vuln.description,
                    'scan_id': vuln.scan.id,
                    'project_name': vuln.scan.project.name
                })
            
            return JsonResponse({'status': 'success', 'vulnerabilities': vulnerabilities})
        except Exception as e:
            print(f"获取工件漏洞失败: {e}")
            return JsonResponse({'status': 'error', 'message': '获取工件漏洞失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

@csrf_exempt
def create_artifact_version_change(request):
    """
    创建工件版本变更记录
    """
    if request.method == 'POST':
        try:
            # 获取请求数据
            data = json.loads(request.body)
            project_id = data.get('project_id')
            artifact_group = data.get('artifact_group')
            artifact_name = data.get('artifact_name')
            old_version = data.get('old_version')
            new_version = data.get('new_version')
            notification_type = data.get('notification_type', 'in_app')
            
            # 验证参数
            if not project_id or not artifact_name or not old_version or not new_version:
                return JsonResponse({'status': 'error', 'message': '缺少必要参数'})
            
            # 获取项目
            project = Project.objects.get(id=project_id)
            
            # 创建工件版本变更记录
            version_change = ArtifactVersionChange.objects.create(
                project=project,
                artifact_group=artifact_group,
                artifact_name=artifact_name,
                old_version=old_version,
                new_version=new_version,
                notification_type=notification_type
            )
            
            # TODO: 实现通知逻辑
            
            return JsonResponse({
                'status': 'success',
                'message': '工件版本变更记录创建成功',
                'version_change_id': version_change.id
            })
        except Exception as e:
            print(f"创建工件版本变更记录失败: {e}")
            return JsonResponse({'status': 'error', 'message': '创建工件版本变更记录失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

def get_project_vulnerability_stats(request):
    """
    获取项目漏洞统计
    """
    if request.method == 'GET':
        try:
            # 获取项目ID
            project_id = request.GET.get('project_id')
            
            # 构建查询
            queryset = ArtifactVulnerability.objects.all()
            
            # 应用过滤
            if project_id:
                queryset = queryset.filter(scan__project_id=project_id)
            
            # 统计漏洞数量
            stats = {
                'critical': queryset.filter(severity='critical').count(),
                'high': queryset.filter(severity='high').count(),
                'medium': queryset.filter(severity='medium').count(),
                'low': queryset.filter(severity='low').count(),
                'info': queryset.filter(severity='info').count(),
                'total': queryset.count()
            }
            
            return JsonResponse({'status': 'success', 'stats': stats})
        except Exception as e:
            print(f"获取项目漏洞统计失败: {e}")
            return JsonResponse({'status': 'error', 'message': '获取项目漏洞统计失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})
