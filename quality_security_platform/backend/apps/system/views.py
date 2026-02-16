from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Notification, SystemConfig
from apps.users.models import User
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

@csrf_exempt
def save_site_settings(request):
    """
    保存网站设置
    """
    if request.method == 'POST':
        try:
            # 获取请求数据
            data = json.loads(request.body)
            
            # 保存配置
            for key, value in data.items():
                config, created = SystemConfig.objects.get_or_create(key=key)
                config.value = value
                config.save()
            
            return JsonResponse({'status': 'success', 'message': '网站设置保存成功'})
        except Exception as e:
            print(f"保存网站设置失败: {e}")
            return JsonResponse({'status': 'error', 'message': '保存网站设置失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

def get_site_settings(request):
    """
    获取网站设置
    """
    if request.method == 'GET':
        try:
            # 获取所有配置
            configs = SystemConfig.objects.all()
            settings = {}
            for config in configs:
                settings[config.key] = config.value
            
            return JsonResponse({'status': 'success', 'settings': settings})
        except Exception as e:
            print(f"获取网站设置失败: {e}")
            return JsonResponse({'status': 'error', 'message': '获取网站设置失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

def upload_company_logo(request):
    """
    上传企业图标
    """
    if request.method == 'POST':
        try:
            # 获取上传的文件
            file = request.FILES.get('file')
            
            # 验证文件
            if not file:
                return JsonResponse({'status': 'error', 'message': '缺少文件'})
            
            # 保存文件到媒体目录
            # 这里需要实现文件保存逻辑
            
            return JsonResponse({'status': 'success', 'message': '企业图标上传成功', 'file_name': file.name})
        except Exception as e:
            print(f"上传企业图标失败: {e}")
            return JsonResponse({'status': 'error', 'message': '上传企业图标失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

def reset_company_logo(request):
    """
    重置企业图标
    """
    if request.method == 'POST':
        try:
            # 这里需要实现重置逻辑
            return JsonResponse({'status': 'success', 'message': '企业图标重置成功'})
        except Exception as e:
            print(f"重置企业图标失败: {e}")
            return JsonResponse({'status': 'error', 'message': '重置企业图标失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

def send_email_notification(request):
    """
    发送邮件通知
    """
    if request.method == 'POST':
        try:
            # 获取请求数据
            data = json.loads(request.body)
            to_email = data.get('to_email')
            subject = data.get('subject')
            content = data.get('content')
            
            # 验证参数
            if not to_email or not subject or not content:
                return JsonResponse({'status': 'error', 'message': '缺少必要参数'})
            
            # 获取邮件配置
            smtp_server = SystemConfig.objects.filter(key='smtp_server').first().value if SystemConfig.objects.filter(key='smtp_server').exists() else ''
            smtp_port = SystemConfig.objects.filter(key='smtp_port').first().value if SystemConfig.objects.filter(key='smtp_port').exists() else '587'
            smtp_username = SystemConfig.objects.filter(key='smtp_username').first().value if SystemConfig.objects.filter(key='smtp_username').exists() else ''
            smtp_password = SystemConfig.objects.filter(key='smtp_password').first().value if SystemConfig.objects.filter(key='smtp_password').exists() else ''
            sender_email = SystemConfig.objects.filter(key='sender_email').first().value if SystemConfig.objects.filter(key='sender_email').exists() else ''
            
            # 发送邮件
            if smtp_server and smtp_username and smtp_password and sender_email:
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = to_email
                msg['Subject'] = subject
                msg.attach(MIMEText(content, 'html', 'utf-8'))
                
                try:
                    server = smtplib.SMTP(smtp_server, int(smtp_port))
                    server.starttls()
                    server.login(smtp_username, smtp_password)
                    server.send_message(msg)
                    server.quit()
                    return JsonResponse({'status': 'success', 'message': '邮件发送成功'})
                except Exception as e:
                    print(f"发送邮件失败: {e}")
                    return JsonResponse({'status': 'error', 'message': '发送邮件失败'})
            else:
                return JsonResponse({'status': 'error', 'message': '邮件配置未完成'})
        except Exception as e:
            print(f"发送邮件通知失败: {e}")
            return JsonResponse({'status': 'error', 'message': '发送邮件通知失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

def get_user_notifications(request):
    """
    获取用户通知
    """
    if request.method == 'GET':
        try:
            # 获取当前用户
            user = request.user
            
            # 获取过滤参数
            is_read = request.GET.get('is_read')
            notification_type = request.GET.get('type')
            
            # 构建查询
            queryset = Notification.objects.filter(user=user).order_by('-created_at')
            
            # 应用过滤
            if is_read is not None:
                queryset = queryset.filter(is_read=is_read == 'true')
            if notification_type:
                queryset = queryset.filter(notification_type=notification_type)
            
            # 构建响应数据
            notifications = []
            for notification in queryset:
                notifications.append({
                    'id': notification.id,
                    'title': notification.title,
                    'content': notification.content,
                    'type': notification.notification_type,
                    'is_read': notification.is_read,
                    'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return JsonResponse({'status': 'success', 'notifications': notifications})
        except Exception as e:
            print(f"获取用户通知失败: {e}")
            return JsonResponse({'status': 'error', 'message': '获取用户通知失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

def mark_notification_read(request, notification_id):
    """
    标记通知为已读
    """
    if request.method == 'PUT':
        try:
            # 获取通知
            notification = Notification.objects.get(id=notification_id, user=request.user)
            
            # 标记为已读
            notification.is_read = True
            notification.save()
            
            return JsonResponse({'status': 'success', 'message': '通知已标记为已读'})
        except Exception as e:
            print(f"标记通知为已读失败: {e}")
            return JsonResponse({'status': 'error', 'message': '标记通知为已读失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

def mark_all_notifications_read(request):
    """
    标记所有通知为已读
    """
    if request.method == 'PUT':
        try:
            # 获取当前用户
            user = request.user
            
            # 标记所有通知为已读
            Notification.objects.filter(user=user, is_read=False).update(is_read=True)
            
            return JsonResponse({'status': 'success', 'message': '所有通知已标记为已读'})
        except Exception as e:
            print(f"标记所有通知为已读失败: {e}")
            return JsonResponse({'status': 'error', 'message': '标记所有通知为已读失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

def delete_notification(request, notification_id):
    """
    删除通知
    """
    if request.method == 'DELETE':
        try:
            # 获取通知
            notification = Notification.objects.get(id=notification_id, user=request.user)
            
            # 删除通知
            notification.delete()
            
            return JsonResponse({'status': 'success', 'message': '通知已删除'})
        except Exception as e:
            print(f"删除通知失败: {e}")
            return JsonResponse({'status': 'error', 'message': '删除通知失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})


from rest_framework.viewsets import ModelViewSet
from .serializers import NotificationSerializer

class NotificationViewSet(ModelViewSet):
    """
    通知视图集
    """
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        """
        获取当前用户的通知
        """
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """
        创建通知
        """
        serializer.save(user=self.request.user)
