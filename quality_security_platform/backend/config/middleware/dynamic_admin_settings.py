from django.contrib import admin
from django.conf import settings
import os
import json

# 配置文件路径
CONFIG_FILE_PATH = os.path.join(settings.BASE_DIR, 'config', 'site_settings.json')

# 默认配置
DEFAULT_SETTINGS = {
    'SITE_HEADER': '质量安全平台',
    'SITE_TITLE': '质量安全平台',
    'COMPANY_LOGO': ''
}

# 读取配置
def read_site_settings():
    """读取网站设置"""
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return DEFAULT_SETTINGS.copy()

class DynamicAdminSettingsMiddleware:
    """
    动态更新Admin站点设置的中间件
    每次请求时都会从配置文件中获取最新的设置
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 每次请求时更新Admin站点设置
        try:
            # 读取配置
            settings_data = read_site_settings()
            
            # 更新Admin站点标题
            admin.site.site_header = settings_data.get('SITE_HEADER', '质量安全平台')
            admin.site.site_title = settings_data.get('SITE_TITLE', '质量安全平台')
            admin.site.index_title = '系统管理'  # 固定为默认值
            
            # 更新SimpleUI Logo
            company_logo = settings_data.get('COMPANY_LOGO', '')
            if company_logo:
                settings.SIMPLEUI_LOGO = f'/media/{company_logo}'
            else:
                settings.SIMPLEUI_LOGO = None
        except Exception:
            # 如果更新失败，保持默认设置
            pass
        
        response = self.get_response(request)
        return response
