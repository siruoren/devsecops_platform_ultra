from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Pipeline, BuildRecord, BuildStageRecord, JenkinsJob, JenkinsBuild, JenkinsBuildParameter, JenkinsCredential
from .services.sonar import SonarQubeService
from .services.jenkins import JenkinsService
import time
import json

@csrf_exempt
def trigger_build(request):
    """
    触发构建
    """
    if request.method == 'POST':
        try:
            # 获取请求数据
            data = json.loads(request.body)
            pipeline_id = data.get('pipeline_id')
            version = data.get('version')
            triggered_by = request.user
            
            # 验证参数
            if not pipeline_id or not version:
                return JsonResponse({'status': 'error', 'message': '缺少必要参数'})
            
            # 获取流水线
            pipeline = Pipeline.objects.get(id=pipeline_id)
            
            # 创建构建记录
            build_record = BuildRecord.objects.create(
                pipeline=pipeline,
                version=version,
                triggered_by=triggered_by,
                status='pending'
            )
            
            # 异步执行构建（实际实现中应该使用 Celery）
            import threading
            threading.Thread(target=execute_build, args=(build_record,)).start()
            
            return JsonResponse({
                'status': 'success',
                'message': '构建已触发',
                'build_id': str(build_record.build_id)
            })
        except Exception as e:
            print(f"触发构建失败: {e}")
            return JsonResponse({'status': 'error', 'message': '触发构建失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

def execute_build(build_record):
    """
    执行构建
    """
    from datetime import datetime
    try:
        # 更新状态为运行中
        build_record.status = 'running'
        build_record.started_at = build_record.started_at or build_record.created_at
        build_record.save()
        
        # 执行每个阶段
        stages = build_record.pipeline.stages.order_by('order')
        for stage in stages:
            # 创建阶段记录
            stage_record = BuildStageRecord.objects.create(
                build=build_record,
                stage=stage,
                status='running'
            )
            
            # 模拟阶段执行
            time.sleep(2)  # 模拟执行时间
            
            # 检查是否是 SonarQube 扫描阶段
            if 'sonar' in stage.name.lower() or 'scan' in stage.name.lower():
                # 集成 SonarQube 扫描
                sonar_service = SonarQubeService()
                project_key = f"{build_record.pipeline.project.name}_{build_record.pipeline.name}"
                project_name = f"{build_record.pipeline.project.name} - {build_record.pipeline.name}"
                
                # 触发 Sonar 扫描
                task_id = sonar_service.trigger_scan(
                    project_key=project_key,
                    project_name=project_name,
                    sources_path='.',
                    branch=build_record.version
                )
                
                # 更新构建记录的 Sonar 任务 ID
                if task_id:
                    build_record.sonar_task_id = task_id
                    build_record.save()
                    
                    # 获取扫描结果
                    sonar_service.update_build_record(build_record, task_id)
            
            # 模拟阶段完成
            stage_record.status = 'success'
            stage_record.save()
        
        # 更新构建状态为成功
        build_record.status = 'success'
        build_record.finished_at = build_record.finished_at or datetime.now()
        if build_record.started_at:
            build_record.duration = int((build_record.finished_at - build_record.started_at).total_seconds())
        else:
            build_record.duration = 0
        build_record.save()
        
        # 发送构建成功通知
        send_build_notification(build_record, 'success')
    except Exception as e:
        print(f"执行构建失败: {e}")
        # 更新构建状态为失败
        build_record.status = 'failed'
        build_record.finished_at = build_record.finished_at or datetime.now()
        build_record.started_at = build_record.started_at or build_record.created_at
        if build_record.started_at:
            build_record.duration = int((build_record.finished_at - build_record.started_at).total_seconds())
        else:
            build_record.duration = 0
        build_record.save()
        
        # 发送构建失败通知
        send_build_notification(build_record, 'failed')

def get_build_history(request):
    """
    获取构建历史
    """
    if request.method == 'GET':
        try:
            # 获取过滤参数
            pipeline_id = request.GET.get('pipeline_id')
            status = request.GET.get('status')
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            
            # 构建查询
            queryset = BuildRecord.objects.all().order_by('-created_at')
            
            # 应用过滤
            if pipeline_id:
                queryset = queryset.filter(pipeline_id=pipeline_id)
            if status:
                queryset = queryset.filter(status=status)
            if start_date:
                queryset = queryset.filter(created_at__gte=start_date)
            if end_date:
                queryset = queryset.filter(created_at__lte=end_date)
            
            # 构建响应数据
            builds = []
            for build in queryset:
                builds.append({
                    'id': build.id,
                    'build_id': str(build.build_id),
                    'pipeline': build.pipeline.name,
                    'pipeline_id': build.pipeline.id,
                    'version': build.version,
                    'status': build.status,
                    'triggered_by': build.triggered_by.username if build.triggered_by else None,
                    'created_at': build.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'started_at': build.started_at.strftime('%Y-%m-%d %H:%M:%S') if build.started_at else None,
                    'finished_at': build.finished_at.strftime('%Y-%m-%d %H:%M:%S') if build.finished_at else None,
                    'duration': build.duration,
                    'sonar_quality_gate': build.sonar_quality_gate
                })
            
            return JsonResponse({'status': 'success', 'builds': builds})
        except Exception as e:
            print(f"获取构建历史失败: {e}")
            return JsonResponse({'status': 'error', 'message': '获取构建历史失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

def get_build_detail(request, build_id):
    """
    获取构建详情
    """
    if request.method == 'GET':
        try:
            # 获取构建记录
            build_record = BuildRecord.objects.get(build_id=build_id)
            
            # 获取阶段记录
            stage_records = BuildStageRecord.objects.filter(build=build_record)
            stages = []
            for stage_record in stage_records:
                stages.append({
                    'id': stage_record.id,
                    'name': stage_record.stage.name,
                    'status': stage_record.status,
                    'started_at': stage_record.started_at.strftime('%Y-%m-%d %H:%M:%S') if stage_record.started_at else None,
                    'finished_at': stage_record.finished_at.strftime('%Y-%m-%d %H:%M:%S') if stage_record.finished_at else None,
                    'log_snippet': stage_record.log_snippet
                })
            
            # 构建响应数据
            build_detail = {
                'id': build_record.id,
                'build_id': str(build_record.build_id),
                'pipeline': build_record.pipeline.name,
                'version': build_record.version,
                'status': build_record.status,
                'triggered_by': build_record.triggered_by.username if build_record.triggered_by else None,
                'created_at': build_record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'started_at': build_record.started_at.strftime('%Y-%m-%d %H:%M:%S') if build_record.started_at else None,
                'finished_at': build_record.finished_at.strftime('%Y-%m-%d %H:%M:%S') if build_record.finished_at else None,
                'duration': build_record.duration,
                'sonar_task_id': build_record.sonar_task_id,
                'sonar_quality_gate': build_record.sonar_quality_gate,
                'log_file': build_record.log_file,
                'stages': stages
            }
            
            return JsonResponse({'status': 'success', 'build': build_detail})
        except Exception as e:
            print(f"获取构建详情失败: {e}")
            return JsonResponse({'status': 'error', 'message': '获取构建详情失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

# Jenkins 任务相关 API

@csrf_exempt
def parse_jenkins_job(request):
    """
    解析 Jenkins 任务
    """
    if request.method == 'POST':
        try:
            # 获取请求数据
            data = json.loads(request.body)
            jenkins_job_id = data.get('jenkins_job_id')
            
            # 验证参数
            if not jenkins_job_id:
                return JsonResponse({'status': 'error', 'message': '缺少必要参数'})
            
            # 获取 Jenkins 任务
            jenkins_job = JenkinsJob.objects.get(id=jenkins_job_id)
            
            # 创建 Jenkins 服务
            jenkins_service = JenkinsService(jenkins_job.credential)
            
            # 解析 Jenkins 任务 URL
            jenkins_url = jenkins_service.parse_jenkins_job_url(jenkins_job.jenkins_url)
            
            # 获取任务参数
            parameters = jenkins_service.get_job_parameters(jenkins_url)
            
            # 保存参数信息
            jenkins_job.parameters = parameters
            jenkins_job.save()
            
            # 删除旧的参数记录
            JenkinsBuildParameter.objects.filter(jenkins_job=jenkins_job).delete()
            
            # 创建新的参数记录
            for param in parameters:
                JenkinsBuildParameter.objects.create(
                    jenkins_job=jenkins_job,
                    name=param.get('name'),
                    display_name=param.get('display_name', param.get('name')),
                    parameter_type=param.get('type'),
                    default_value=param.get('default_value', ''),
                    choices=param.get('choices', []),
                    description=param.get('description', ''),
                    is_required=True
                )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Jenkins 任务解析成功',
                'parameters': parameters
            })
        except Exception as e:
            print(f"解析 Jenkins 任务失败: {e}")
            return JsonResponse({'status': 'error', 'message': '解析 Jenkins 任务失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

@csrf_exempt
def trigger_jenkins_build(request):
    """
    触发 Jenkins 构建
    """
    if request.method == 'POST':
        try:
            # 获取请求数据
            data = json.loads(request.body)
            jenkins_job_id = data.get('jenkins_job_id')
            parameters = data.get('parameters', {})
            triggered_by = request.user
            
            # 验证参数
            if not jenkins_job_id:
                return JsonResponse({'status': 'error', 'message': '缺少必要参数'})
            
            # 获取 Jenkins 任务
            jenkins_job = JenkinsJob.objects.get(id=jenkins_job_id)
            
            # 创建 Jenkins 服务
            jenkins_service = JenkinsService(jenkins_job.credential)
            
            # 触发构建
            build_number = jenkins_service.trigger_build(jenkins_job.jenkins_url, parameters)
            
            if not build_number:
                return JsonResponse({'status': 'error', 'message': '触发 Jenkins 构建失败'})
            
            # 创建构建记录
            jenkins_build = JenkinsBuild.objects.create(
                jenkins_job=jenkins_job,
                jenkins_build_number=build_number,
                jenkins_build_url=f"{jenkins_job.jenkins_url}build/{build_number}/",
                parameters=parameters,
                status='running',
                triggered_by=triggered_by,
                started_at=time.strftime('%Y-%m-%d %H:%M:%S')
            )
            
            # 异步追踪构建状态（实际实现中应该使用 Celery）
            import threading
            threading.Thread(target=track_jenkins_build, args=(jenkins_build, jenkins_service)).start()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Jenkins 构建已触发',
                'build_id': str(jenkins_build.build_id),
                'jenkins_build_number': build_number
            })
        except Exception as e:
            print(f"触发 Jenkins 构建失败: {e}")
            return JsonResponse({'status': 'error', 'message': '触发 Jenkins 构建失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

def track_jenkins_build(jenkins_build, jenkins_service):
    """
    追踪 Jenkins 构建状态
    """
    try:
        # 追踪构建状态，直到完成
        while True:
            # 获取构建状态
            status = jenkins_service.get_build_status(
                jenkins_build.jenkins_job.jenkins_url,
                jenkins_build.jenkins_build_number
            )
            
            # 更新构建状态
            jenkins_build.status = status
            
            # 获取构建日志
            log = jenkins_service.get_build_log(
                jenkins_build.jenkins_job.jenkins_url,
                jenkins_build.jenkins_build_number
            )
            jenkins_build.log = log
            
            # 检查构建是否完成
            if status in ['success', 'failed', 'aborted']:
                jenkins_build.finished_at = time.strftime('%Y-%m-%d %H:%M:%S')
                # 计算构建时长
                if jenkins_build.started_at:
                    start_time = time.mktime(time.strptime(jenkins_build.started_at, '%Y-%m-%d %H:%M:%S'))
                    end_time = time.mktime(time.strptime(jenkins_build.finished_at, '%Y-%m-%d %H:%M:%S'))
                    jenkins_build.duration = int(end_time - start_time)
                jenkins_build.save()
                break
            
            jenkins_build.save()
            # 等待一段时间后再次检查
            time.sleep(5)
    except Exception as e:
        print(f"追踪 Jenkins 构建失败: {e}")
        # 更新构建状态为失败
        jenkins_build.status = 'failed'
        jenkins_build.finished_at = time.strftime('%Y-%m-%d %H:%M:%S')
        jenkins_build.save()

def get_jenkins_jobs(request):
    """
    获取 Jenkins 任务列表
    """
    if request.method == 'GET':
        try:
            # 获取过滤参数
            is_active = request.GET.get('is_active')
            
            # 构建查询
            queryset = JenkinsJob.objects.all().order_by('-created_at')
            
            # 应用过滤
            if is_active:
                queryset = queryset.filter(is_active=is_active == 'true')
            
            # 构建响应数据
            jobs = []
            for job in queryset:
                jobs.append({
                    'id': job.id,
                    'name': job.name,
                    'description': job.description,
                    'jenkins_url': job.jenkins_url,
                    'credential': job.credential.name,
                    'pipeline': job.pipeline.name if job.pipeline else None,
                    'is_active': job.is_active,
                    'created_at': job.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'parameter_count': job.build_parameters.count()
                })
            
            return JsonResponse({'status': 'success', 'jobs': jobs})
        except Exception as e:
            print(f"获取 Jenkins 任务列表失败: {e}")
            return JsonResponse({'status': 'error', 'message': '获取 Jenkins 任务列表失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

def get_jenkins_job_parameters(request, job_id):
    """
    获取 Jenkins 任务参数
    """
    if request.method == 'GET':
        try:
            # 获取 Jenkins 任务
            jenkins_job = JenkinsJob.objects.get(id=job_id)
            
            # 获取参数
            parameters = []
            for param in jenkins_job.build_parameters.all():
                parameters.append({
                    'id': param.id,
                    'name': param.name,
                    'display_name': param.display_name,
                    'parameter_type': param.parameter_type,
                    'default_value': param.default_value,
                    'choices': param.choices,
                    'description': param.description,
                    'is_required': param.is_required
                })
            
            return JsonResponse({'status': 'success', 'parameters': parameters})
        except Exception as e:
            print(f"获取 Jenkins 任务参数失败: {e}")
            return JsonResponse({'status': 'error', 'message': '获取 Jenkins 任务参数失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

def get_jenkins_build_history(request):
    """
    获取 Jenkins 构建历史
    """
    if request.method == 'GET':
        try:
            # 获取过滤参数
            jenkins_job_id = request.GET.get('jenkins_job_id')
            status = request.GET.get('status')
            
            # 构建查询
            queryset = JenkinsBuild.objects.all().order_by('-created_at')
            
            # 应用过滤
            if jenkins_job_id:
                queryset = queryset.filter(jenkins_job_id=jenkins_job_id)
            if status:
                queryset = queryset.filter(status=status)
            
            # 构建响应数据
            builds = []
            for build in queryset:
                builds.append({
                    'id': build.id,
                    'build_id': str(build.build_id),
                    'jenkins_job': build.jenkins_job.name,
                    'jenkins_build_number': build.jenkins_build_number,
                    'jenkins_build_url': build.jenkins_build_url,
                    'parameters': build.parameters,
                    'status': build.status,
                    'triggered_by': build.triggered_by.username if build.triggered_by else None,
                    'started_at': build.started_at.strftime('%Y-%m-%d %H:%M:%S') if build.started_at else None,
                    'finished_at': build.finished_at.strftime('%Y-%m-%d %H:%M:%S') if build.finished_at else None,
                    'duration': build.duration
                })
            
            return JsonResponse({'status': 'success', 'builds': builds})
        except Exception as e:
            print(f"获取 Jenkins 构建历史失败: {e}")
            return JsonResponse({'status': 'error', 'message': '获取 Jenkins 构建历史失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})

def get_jenkins_build_detail(request, build_id):
    """
    获取 Jenkins 构建详情
    """
    if request.method == 'GET':
        try:
            # 获取构建记录
            jenkins_build = JenkinsBuild.objects.get(build_id=build_id)
            
            # 构建响应数据
            build_detail = {
                'id': jenkins_build.id,
                'build_id': str(jenkins_build.build_id),
                'jenkins_job': jenkins_build.jenkins_job.name,
                'jenkins_build_number': jenkins_build.jenkins_build_number,
                'jenkins_build_url': jenkins_build.jenkins_build_url,
                'parameters': jenkins_build.parameters,
                'status': jenkins_build.status,
                'log': jenkins_build.log,
                'triggered_by': jenkins_build.triggered_by.username if jenkins_build.triggered_by else None,
                'started_at': jenkins_build.started_at.strftime('%Y-%m-%d %H:%M:%S') if jenkins_build.started_at else None,
                'finished_at': jenkins_build.finished_at.strftime('%Y-%m-%d %H:%M:%S') if jenkins_build.finished_at else None,
                'duration': jenkins_build.duration
            }
            
            return JsonResponse({'status': 'success', 'build': build_detail})
        except Exception as e:
            print(f"获取 Jenkins 构建详情失败: {e}")
            return JsonResponse({'status': 'error', 'message': '获取 Jenkins 构建详情失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})


def get_jenkins_credentials(request):
    """
    获取 Jenkins 凭证列表
    """
    if request.method == 'GET':
        try:
            # 获取所有活跃的凭证
            credentials = JenkinsCredential.objects.filter(is_active=True)
            
            # 构建响应数据
            credential_list = []
            for credential in credentials:
                credential_list.append({
                    'id': credential.id,
                    'name': credential.name,
                    'url': credential.url,
                    'description': credential.description,
                    'is_active': credential.is_active
                })
            
            return JsonResponse({'status': 'success', 'credentials': credential_list})
        except Exception as e:
            print(f"获取 Jenkins 凭证失败: {e}")
            return JsonResponse({'status': 'error', 'message': '获取 Jenkins 凭证失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})


def create_jenkins_job(request):
    """
    创建 Jenkins 任务
    """
    if request.method == 'POST':
        try:
            # 获取请求数据
            data = json.loads(request.body)
            name = data.get('name')
            description = data.get('description', '')
            jenkins_url = data.get('jenkins_url')
            credential_id = data.get('credential')
            pipeline_id = data.get('pipeline')
            
            # 验证参数
            if not name or not jenkins_url or not credential_id:
                return JsonResponse({'status': 'error', 'message': '缺少必要参数'})
            
            # 获取凭证
            credential = JenkinsCredential.objects.get(id=credential_id)
            
            # 获取流水线
            pipeline = None
            if pipeline_id:
                pipeline = Pipeline.objects.get(id=pipeline_id)
            
            # 创建 Jenkins 任务
            jenkins_job = JenkinsJob.objects.create(
                name=name,
                description=description,
                jenkins_url=jenkins_url,
                credential=credential,
                pipeline=pipeline,
                created_by=request.user
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Jenkins 任务创建成功',
                'job_id': jenkins_job.id
            })
        except Exception as e:
            print(f"创建 Jenkins 任务失败: {e}")
            return JsonResponse({'status': 'error', 'message': '创建 Jenkins 任务失败'})
    
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})


def start_build(request, pipeline_id):
    """
    开始构建流水线（用于Admin页面）
    """
    try:
        from django.shortcuts import redirect
        from django.urls import reverse
        
        # 检查用户是否登录
        if not request.user.is_authenticated:
            print("用户未登录")
            return redirect(reverse('admin:login'))
        
        # 获取流水线
        pipeline = Pipeline.objects.get(id=pipeline_id)
        print(f"开始构建流水线: {pipeline.name}")
        
        # 触发构建
        build_record = BuildRecord.objects.create(
            pipeline=pipeline,
            version='latest',
            triggered_by=request.user,
            status='pending'
        )
        print(f"创建构建记录: {build_record.build_id}")
        
        # 异步执行构建
        import threading
        print("启动异步构建线程")
        threading.Thread(target=execute_build, args=(build_record,)).start()
        
        # 重定向回流水线管理页面
        return redirect(reverse('admin:ci_cd_pipeline_changelist'))
    except Exception as e:
        print(f"开始构建失败: {e}")
        from django.shortcuts import redirect
        from django.urls import reverse
        return redirect(reverse('admin:ci_cd_pipeline_changelist'))


def cancel_build(request, pipeline_id):
    """
    取消构建流水线（用于Admin页面）
    """
    try:
        from django.shortcuts import redirect
        from django.urls import reverse
        
        # 获取流水线
        pipeline = Pipeline.objects.get(id=pipeline_id)
        
        # 取消当前正在运行的构建
        running_builds = BuildRecord.objects.filter(
            pipeline=pipeline,
            status__in=['running', 'pending']
        )
        
        for build in running_builds:
            build.status = 'aborted'
            build.finished_at = build.finished_at or build.created_at
            build.save()
        
        # 重定向回流水线管理页面
        return redirect(reverse('admin:ci_cd_pipeline_changelist'))
    except Exception as e:
        print(f"取消构建失败: {e}")
        from django.shortcuts import redirect
        from django.urls import reverse
        return redirect(reverse('admin:ci_cd_pipeline_changelist'))


def send_email_notification_raw(to_email, subject, content):
    """
    发送邮件通知（无请求上下文）
    """
    try:
        from apps.system.models import SystemConfig
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
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
                return True
            except Exception as e:
                print(f"发送邮件失败: {e}")
                return False
        else:
            print("邮件配置未完成")
            return False
    except Exception as e:
        print(f"发送邮件通知失败: {e}")
        return False


def send_build_notification(build_record, status):
    """
    发送构建通知
    """
    try:
        from apps.system.models import Notification
        
        # 获取触发人
        triggered_by = build_record.triggered_by
        if not triggered_by:
            return
        
        # 构建通知内容
        if status == 'success':
            title = f"构建成功: {build_record.pipeline.name}"
            content = f"流水线 {build_record.pipeline.name} 的构建已成功完成\n版本: {build_record.version}\n构建时间: {build_record.duration} 秒"
            email_content = f"<h3>构建成功通知</h3><p>流水线 <strong>{build_record.pipeline.name}</strong> 的构建已成功完成</p><p><strong>版本:</strong> {build_record.version}</p><p><strong>构建时间:</strong> {build_record.duration} 秒</p><p><strong>触发人:</strong> {triggered_by.username}</p>"
        else:
            title = f"构建失败: {build_record.pipeline.name}"
            content = f"流水线 {build_record.pipeline.name} 的构建失败\n版本: {build_record.version}\n请查看构建日志了解详情"
            email_content = f"<h3>构建失败通知</h3><p>流水线 <strong>{build_record.pipeline.name}</strong> 的构建失败</p><p><strong>版本:</strong> {build_record.version}</p><p><strong>触发人:</strong> {triggered_by.username}</p><p>请查看构建日志了解详情</p>"
        
        # 创建站内通知
        Notification.objects.create(
            user=triggered_by,
            title=title,
            content=content,
            notification_type='pipeline'
        )
        
        # 发送邮件通知
        if triggered_by and triggered_by.email:
            send_email_notification_raw(
                to_email=triggered_by.email,
                subject=title,
                content=email_content
            )
    except Exception as e:
        print(f"发送构建通知失败: {e}")
