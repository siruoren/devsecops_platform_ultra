from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ReleaseVersion, VersionRegistration
import json
from django.shortcuts import get_object_or_404

@csrf_exempt
def get_versions(request):
    """
    获取所有发布版本
    """
    if request.method == 'GET':
        try:
            versions = ReleaseVersion.objects.all().order_by('-created_at')
            version_list = []
            for version in versions:
                version_data = {
                    'id': version.id,
                    'version': version.version,
                    'created_at': version.created_at.isoformat(),
                    'released_at': version.released_at.isoformat() if version.released_at else None,
                    'status': version.status,
                    'code_quality': version.code_quality,
                    'registrations': [
                        {
                            'project': reg.project.name,
                            'app_version': reg.app_version
                        }
                        for reg in version.registrations.all()
                    ]
                }
                version_list.append(version_data)
            return JsonResponse({'status': 'success', 'results': version_list})
        except Exception as e:
            print(f"获取版本列表失败: {e}")
            return JsonResponse({'status': 'error', 'message': '获取版本列表失败'})
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

@csrf_exempt
def get_version_detail(request, version_id):
    """
    获取版本详情，包括登记的应用版本
    """
    if request.method == 'GET':
        try:
            version = get_object_or_404(ReleaseVersion, id=version_id)
            registrations = VersionRegistration.objects.filter(release_version=version)
            registration_list = []
            for reg in registrations:
                registration_list.append({
                    'id': reg.id,
                    'project': reg.project.name,
                    'app_version': reg.app_version,
                    'created_by': reg.created_by.username if reg.created_by else None,
                    'created_at': reg.created_at.isoformat()
                })
            version_data = {
                'id': version.id,
                'version': version.version,
                'created_at': version.created_at.isoformat(),
                'released_at': version.released_at.isoformat() if version.released_at else None,
                'status': version.status,
                'code_quality': version.code_quality,
                'registrations': registration_list
            }
            return JsonResponse({'status': 'success', 'data': version_data})
        except Exception as e:
            print(f"获取版本详情失败: {e}")
            return JsonResponse({'status': 'error', 'message': '获取版本详情失败'})
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

@csrf_exempt
def create_version(request):
    """
    创建发布版本
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            version_number = data.get('version')
            status = data.get('status', 'developing')
            
            if not version_number:
                return JsonResponse({'status': 'error', 'message': '版本号不能为空'})
            
            # 检查版本号是否已存在
            if ReleaseVersion.objects.filter(version=version_number).exists():
                return JsonResponse({'status': 'error', 'message': '版本号已存在'})
            
            version = ReleaseVersion.objects.create(
                version=version_number,
                status=status,
                created_by=request.user if request.user.is_authenticated else None
            )
            
            return JsonResponse({'status': 'success', 'message': '版本创建成功', 'data': {'id': version.id, 'version': version.version}})
        except Exception as e:
            print(f"创建版本失败: {e}")
            return JsonResponse({'status': 'error', 'message': '创建版本失败'})
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

@csrf_exempt
def update_version(request, version_id):
    """
    更新发布版本
    """
    if request.method == 'PUT':
        try:
            version = get_object_or_404(ReleaseVersion, id=version_id)
            data = json.loads(request.body)
            
            if 'version' in data:
                # 检查版本号是否已存在（排除当前版本）
                if ReleaseVersion.objects.filter(version=data['version']).exclude(id=version_id).exists():
                    return JsonResponse({'status': 'error', 'message': '版本号已存在'})
                version.version = data['version']
            
            if 'status' in data:
                version.status = data['status']
                # 如果状态变为已封板，设置封板时间
                if data['status'] == 'released' and not version.released_at:
                    from django.utils import timezone
                    version.released_at = timezone.now()
            
            version.save()
            
            return JsonResponse({'status': 'success', 'message': '版本更新成功', 'data': {'id': version.id, 'version': version.version}})
        except Exception as e:
            print(f"更新版本失败: {e}")
            return JsonResponse({'status': 'error', 'message': '更新版本失败'})
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

@csrf_exempt
def delete_version(request, version_id):
    """
    删除发布版本
    """
    if request.method == 'DELETE':
        try:
            version = get_object_or_404(ReleaseVersion, id=version_id)
            version.delete()
            return JsonResponse({'status': 'success', 'message': '版本删除成功'})
        except Exception as e:
            print(f"删除版本失败: {e}")
            return JsonResponse({'status': 'error', 'message': '删除版本失败'})
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

@csrf_exempt
def create_version_registration(request):
    """
    创建版本登记
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            release_version_id = data.get('release_version_id')
            project_id = data.get('project_id')
            app_version = data.get('app_version')
            
            if not all([release_version_id, project_id, app_version]):
                return JsonResponse({'status': 'error', 'message': '缺少必要参数'})
            
            # 检查是否已存在登记记录
            if VersionRegistration.objects.filter(
                release_version_id=release_version_id,
                project_id=project_id
            ).exists():
                return JsonResponse({'status': 'error', 'message': '该应用已在版本中登记'})
            
            from apps.projects.models import Project
            release_version = get_object_or_404(ReleaseVersion, id=release_version_id)
            project = get_object_or_404(Project, id=project_id)
            
            registration = VersionRegistration.objects.create(
                release_version=release_version,
                project=project,
                app_version=app_version,
                created_by=request.user if request.user.is_authenticated else None
            )
            
            return JsonResponse({
                'status': 'success', 
                'message': '版本登记成功',
                'data': {
                    'id': registration.id,
                    'project': project.name,
                    'app_version': registration.app_version
                }
            })
        except Exception as e:
            print(f"创建版本登记失败: {e}")
            return JsonResponse({'status': 'error', 'message': '创建版本登记失败'})
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

@csrf_exempt
def update_version_registration(request, registration_id):
    """
    更新版本登记
    """
    if request.method == 'PUT':
        try:
            registration = get_object_or_404(VersionRegistration, id=registration_id)
            data = json.loads(request.body)
            
            if 'app_version' in data:
                registration.app_version = data['app_version']
            
            registration.save()
            
            return JsonResponse({
                'status': 'success', 
                'message': '版本登记更新成功',
                'data': {
                    'id': registration.id,
                    'project': registration.project.name,
                    'app_version': registration.app_version
                }
            })
        except Exception as e:
            print(f"更新版本登记失败: {e}")
            return JsonResponse({'status': 'error', 'message': '更新版本登记失败'})
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

@csrf_exempt
def delete_version_registration(request, registration_id):
    """
    删除版本登记
    """
    if request.method == 'DELETE':
        try:
            registration = get_object_or_404(VersionRegistration, id=registration_id)
            registration.delete()
            return JsonResponse({'status': 'success', 'message': '版本登记删除成功'})
        except Exception as e:
            print(f"删除版本登记失败: {e}")
            return JsonResponse({'status': 'error', 'message': '删除版本登记失败'})
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})
