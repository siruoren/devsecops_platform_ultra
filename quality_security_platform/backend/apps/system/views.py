from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
from rest_framework import viewsets
from .models import Notification
from .serializers import NotificationSerializer
from apps.base.viewsets import BaseModelViewSet

class NotificationViewSet(BaseModelViewSet):
    """通知管理视图集"""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Notification.objects.all()
        return Notification.objects.filter(recipient=user)

@csrf_exempt
def upload_company_logo(request):
    """上传企业图标"""
    if request.method == 'POST' and request.FILES.get('logo'):
        logo = request.FILES['logo']
        
        # 验证文件类型
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg']
        ext = os.path.splitext(logo.name)[1].lower()
        if ext not in allowed_extensions:
            return JsonResponse({'status': 'error', 'message': '只支持 JPG、PNG、GIF、SVG 图片格式'})
        
        # 验证文件大小（限制为 5MB）
        if logo.size > 5 * 1024 * 1024:
            return JsonResponse({'status': 'error', 'message': '文件大小不能超过 5MB'})
        
        # 确保上传目录存在
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'logos')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        fs = FileSystemStorage(location=upload_dir)
        filename = fs.save(logo.name, logo)
        
        # 更新 CONSTANCE 配置
        try:
            from constance import config
            config.COMPANY_LOGO = os.path.join('logos', filename)
        except Exception as e:
            print(f"更新配置失败: {e}")
        
        return JsonResponse({'status': 'success', 'message': '企业图标上传成功', 'logo_url': os.path.join(settings.MEDIA_URL, 'logos', filename)})
    
    return JsonResponse({'status': 'error', 'message': '上传失败，请检查文件'})

@csrf_exempt
def save_site_settings(request):
    """保存网站设置"""
    if request.method == 'POST':
        # 获取表单数据
        site_header = request.POST.get('site_header')
        site_title = request.POST.get('site_title')
        
        # 保存到系统配置
        try:
            # 使用 Constance 配置保存网站标题设置
            from constance import config
            config.SITE_HEADER = site_header
            config.SITE_TITLE = site_title
            
            return JsonResponse({'status': 'success', 'message': '网站标题设置保存成功'})
        except Exception as e:
            print(f"保存配置失败: {e}")
            return JsonResponse({'status': 'error', 'message': '保存配置失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

@csrf_exempt
def get_site_settings(request):
    """获取当前网站设置配置"""
    if request.method == 'GET':
        try:
            from constance import config
            # 返回当前配置值
            config_data = {
                'SITE_HEADER': getattr(config, 'SITE_HEADER', '质量安全平台'),
                'SITE_TITLE': getattr(config, 'SITE_TITLE', '质量安全平台'),
                'COMPANY_LOGO': getattr(config, 'COMPANY_LOGO', '')
            }
            return JsonResponse({'status': 'success', 'config': config_data})
        except Exception as e:
            print(f"获取配置失败: {e}")
            return JsonResponse({'status': 'error', 'message': '获取配置失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

@csrf_exempt
def reset_company_logo(request):
    """重置企业图标为默认值"""
    if request.method == 'POST':
        try:
            from constance import config
            # 重置为默认值（空字符串）
            config.COMPANY_LOGO = ''
            return JsonResponse({'status': 'success', 'message': '企业图标已重置为默认值'})
        except Exception as e:
            print(f"重置配置失败: {e}")
            return JsonResponse({'status': 'error', 'message': '重置失败，请重试'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})
