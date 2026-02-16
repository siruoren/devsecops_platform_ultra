from django.urls import path
from . import views

app_name = 'cicd'

urlpatterns = [
    # 触发构建
    path('trigger-build/', views.trigger_build, name='trigger_build'),
    # 获取构建历史
    path('build-history/', views.get_build_history, name='get_build_history'),
    # 获取构建详情
    path('build-detail/<uuid:build_id>/', views.get_build_detail, name='get_build_detail'),
    
    # Jenkins 任务相关 API
    # 获取 Jenkins 任务列表
    path('jenkins-jobs/', views.get_jenkins_jobs, name='get_jenkins_jobs'),
    # 创建 Jenkins 任务
    path('jenkins-jobs/create/', views.create_jenkins_job, name='create_jenkins_job'),
    # 解析 Jenkins 任务
    path('parse-jenkins-job/', views.parse_jenkins_job, name='parse_jenkins_job'),
    # 获取 Jenkins 任务参数
    path('jenkins-job-parameters/<int:job_id>/', views.get_jenkins_job_parameters, name='get_jenkins_job_parameters'),
    # 触发 Jenkins 构建
    path('trigger-jenkins-build/', views.trigger_jenkins_build, name='trigger_jenkins_build'),
    # 获取 Jenkins 构建历史
    path('jenkins-build-history/', views.get_jenkins_build_history, name='get_jenkins_build_history'),
    # 获取 Jenkins 构建详情
    path('jenkins-build-detail/<uuid:build_id>/', views.get_jenkins_build_detail, name='get_jenkins_build_detail'),
    # 获取 Jenkins 凭证列表
    path('jenkins-credentials/', views.get_jenkins_credentials, name='get_jenkins_credentials'),
    
    # 开始构建（用于Admin页面）
    path('start-build/<int:pipeline_id>/', views.start_build, name='start_build'),
    # 取消构建（用于Admin页面）
    path('cancel-build/<int:pipeline_id>/', views.cancel_build, name='cancel_build'),
]
