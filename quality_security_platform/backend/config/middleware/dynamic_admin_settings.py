from django.contrib import admin
from django.conf import settings
from apps.system.models import SystemConfig

# 默认配置
DEFAULT_SETTINGS = {
    'SITE_HEADER': '质量安全平台',
    'SITE_TITLE': '质量安全平台',
    'COMPANY_LOGO': ''
}

# 读取配置
def read_site_settings():
    """从数据库中读取网站设置"""
    try:
        # 从数据库中获取所有配置
        configs = SystemConfig.objects.all()
        settings_data = {}
        for config in configs:
            settings_data[config.key] = config.value
        
        # 如果没有配置，使用默认值
        if not settings_data:
            return DEFAULT_SETTINGS.copy()
        
        return settings_data
    except Exception:
        # 如果数据库连接失败，使用默认配置
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
