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
        
        # 确保上传目录存在
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'logos')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        fs = FileSystemStorage(location=upload_dir)
        filename = fs.save(logo.name, logo)
        
        # 更新 CONSTANCE 配置
        from constance import config
        config.COMPANY_LOGO = os.path.join('logos', filename)
        
        return JsonResponse({'status': 'success', 'message': '企业图标上传成功', 'logo_url': os.path.join(settings.MEDIA_URL, 'logos', filename)})
    
    return JsonResponse({'status': 'error', 'message': '上传失败，请检查文件'})
