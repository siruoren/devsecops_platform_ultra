from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BuildRecord
from apps.system.models import Notification
from django.conf import settings
import os
import json

@receiver(post_save, sender=BuildRecord)
def build_status_changed(sender, instance, created, **kwargs):
    """
    构建状态变更时的信号处理器
    当构建失败时，自动发送通知
    """
    # 只处理状态变更，不处理创建
    if not created:
        # 检查状态是否变为失败
        if instance.status == 'failed':
            # 发送站内消息通知
            send_build_failed_notification(instance)
            # 发送邮件通知（如果配置）
            send_build_failed_email(instance)

def send_build_failed_notification(build_record):
    """
    发送构建失败的站内消息通知
    """
    try:
        # 获取触发人
        triggered_by = build_record.triggered_by
        if not triggered_by:
            return
        
        # 创建通知内容
        title = f'构建失败通知 - {build_record.pipeline.name}'
        content = f'''
        构建 ID: {build_record.build_id}
        流水线: {build_record.pipeline.name}
        版本/分支: {build_record.version}
        状态: 失败
        触发人: {triggered_by.username}
        创建时间: {build_record.created_at.strftime('%Y-%m-%d %H:%M:%S')}
        
        请查看构建详情了解失败原因。
        '''
        
        # 创建通知
        Notification.objects.create(
            recipient=triggered_by,
            title=title,
            content=content
        )
    except Exception as e:
        print(f"发送构建失败通知失败: {e}")

def send_build_failed_email(build_record):
    """
    发送构建失败的邮件通知
    """
    try:
        # 检查是否配置了邮件设置
        CONFIG_FILE_PATH = os.path.join(settings.BASE_DIR, 'config', 'site_settings.json')
        
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            # 检查是否配置了SMTP设置
            # 这里需要检查Constance配置中的SMTP设置
            # 由于我们已经移除了Constance中的SMTP设置，需要从其他地方获取
            # 暂时跳过邮件发送，后续可以添加邮件配置
            pass
    except Exception as e:
        print(f"发送构建失败邮件失败: {e}")
