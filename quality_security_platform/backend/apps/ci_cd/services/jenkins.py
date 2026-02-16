import requests
import time
import json
import re
from urllib.parse import urljoin
from django.conf import settings

class JenkinsService:
    """
    Jenkins服务类
    用于与Jenkins API交互，实现任务解析、构建调度等功能
    """
    
    def __init__(self, credential):
        """
        初始化Jenkins服务
        """
        self.credential = credential
        self.base_url = credential.url.rstrip('/')
        self.username = credential.username
        self.password = credential.password
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def _get(self, endpoint, params=None):
        """
        发送GET请求
        """
        url = urljoin(self.base_url, endpoint)
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Jenkins GET请求失败: {e}")
            return None
    
    def _post(self, endpoint, data=None):
        """
        发送POST请求
        """
        url = urljoin(self.base_url, endpoint)
        try:
            response = self.session.post(url, json=data, timeout=30)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"Jenkins POST请求失败: {e}")
            return None
    
    def get_job_info(self, job_url):
        """
        获取Jenkins任务信息
        """
        try:
            # 从URL中提取任务名称
            job_name = job_url.rstrip('/').split('/')[-1]
            endpoint = f'/job/{job_name}/api/json'
            return self._get(endpoint)
        except Exception as e:
            print(f"获取Jenkins任务信息失败: {e}")
            return None
    
    def get_job_parameters(self, job_url):
        """
        获取Jenkins任务参数
        """
        try:
            job_info = self.get_job_info(job_url)
            if not job_info:
                return []
            
            parameters = []
            if 'actions' in job_info:
                for action in job_info['actions']:
                    if '_class' in action and action['_class'] == 'hudson.model.ParametersDefinitionProperty':
                        if 'parameterDefinitions' in action:
                            for param_def in action['parameterDefinitions']:
                                param_info = {
                                    'name': param_def.get('name'),
                                    'display_name': param_def.get('description', param_def.get('name')),
                                    'type': param_def.get('type', 'StringParameterDefinition').split('.')[-1],
                                    'default_value': param_def.get('defaultValue', ''),
                                    'description': param_def.get('description', ''),
                                    'choices': []
                                }
                                
                                # 处理选项参数
                                if 'choices' in param_def:
                                    param_info['choices'] = param_def['choices']
                                
                                parameters.append(param_info)
            
            return parameters
        except Exception as e:
            print(f"获取Jenkins任务参数失败: {e}")
            return []
    
    def trigger_build(self, job_url, parameters=None):
        """
        触发Jenkins构建
        """
        try:
            # 从URL中提取任务名称
            job_name = job_url.rstrip('/').split('/')[-1]
            endpoint = f'/job/{job_name}/build'
            
            # 构建参数
            data = {}
            if parameters:
                data['parameters'] = []
                for param_name, param_value in parameters.items():
                    data['parameters'].append({
                        'name': param_name,
                        'value': param_value
                    })
            
            response = self._post(endpoint, data)
            if response and response.status_code == 201:
                # 从响应头中获取构建URL
                location = response.headers.get('Location')
                if location:
                    # 获取构建编号
                    build_number = re.search(r'/build/([0-9]+)/', location)
                    if build_number:
                        return int(build_number.group(1))
            
            return None
        except Exception as e:
            print(f"触发Jenkins构建失败: {e}")
            return None
    
    def get_build_info(self, job_url, build_number):
        """
        获取Jenkins构建信息
        """
        try:
            job_name = job_url.rstrip('/').split('/')[-1]
            endpoint = f'/job/{job_name}/{build_number}/api/json'
            return self._get(endpoint)
        except Exception as e:
            print(f"获取Jenkins构建信息失败: {e}")
            return None
    
    def get_build_log(self, job_url, build_number, start=0, length=10000):
        """
        获取Jenkins构建日志
        """
        try:
            job_name = job_url.rstrip('/').split('/')[-1]
            endpoint = f'/job/{job_name}/{build_number}/consoleText'
            url = urljoin(self.base_url, endpoint)
            params = {'start': start, 'length': length}
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"获取Jenkins构建日志失败: {e}")
            return ''
    
    def get_build_status(self, job_url, build_number):
        """
        获取Jenkins构建状态
        """
        try:
            build_info = self.get_build_info(job_url, build_number)
            if not build_info:
                return 'pending'
            
            result = build_info.get('result')
            building = build_info.get('building', False)
            
            if building:
                return 'running'
            elif result == 'SUCCESS':
                return 'success'
            elif result == 'FAILURE':
                return 'failed'
            elif result == 'ABORTED':
                return 'aborted'
            else:
                return 'pending'
        except Exception as e:
            print(f"获取Jenkins构建状态失败: {e}")
            return 'pending'
    
    def parse_jenkins_job_url(self, job_url):
        """
        解析Jenkins任务URL
        """
        try:
            # 标准化URL
            job_url = job_url.rstrip('/')
            
            # 确保URL指向任务页面
            if not job_url.endswith('/'):
                job_url += '/'
            
            return job_url
        except Exception as e:
            print(f"解析Jenkins任务URL失败: {e}")
            return job_url
