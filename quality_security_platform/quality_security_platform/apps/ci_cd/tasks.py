from celery import shared_task
import time
@shared_task(bind=True, max_retries=3)
def run_pipeline(self, pipeline_id, version, user_id):
    from .models import Pipeline, BuildRecord, BuildStageRecord
    from django.utils import timezone
    pipeline = Pipeline.objects.get(id=pipeline_id)
    build = BuildRecord.objects.create(
        pipeline=pipeline,
        version=version,
        status='running',
        triggered_by_id=user_id,
        started_at=timezone.now()
    )
    try:
        # 按顺序执行阶段
        for stage in pipeline.stages.all():
            stage_record = BuildStageRecord.objects.create(
                build=build,
                stage=stage,
                status='running',
                started_at=timezone.now()
            )
            # 模拟执行
            time.sleep(2)
            stage_record.status = 'success'
            stage_record.finished_at = timezone.now()
            stage_record.save()
        build.status = 'success'
    except Exception as e:
        build.status = 'failed'
        raise self.retry(exc=e)
    finally:
        build.finished_at = timezone.now()
        build.duration = (build.finished_at - build.started_at).seconds
        build.save()
    return build.id
@shared_task
def send_build_notification(build_id):
    """构建失败通知"""
    from .models import BuildRecord
    from apps.system.models import Notification
    from constance import config
    build = BuildRecord.objects.get(id=build_id)
    if build.status == 'failed':
        # 发送站内信
        Notification.objects.create(
            recipient=build.triggered_by,
            sender=None,
            title=f'构建失败: {build.pipeline.name}',
            content=f'构建 #{build.build_id} 失败，请检查日志。'
        )
        # 发送邮件 (略)
