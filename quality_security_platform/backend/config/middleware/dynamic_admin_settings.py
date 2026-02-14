from django.contrib import admin
from django.conf import settings

try:
    from constance import config
except ImportError:
    config = None

class DynamicAdminSettingsMiddleware:
    """
    动态更新Admin站点设置的中间件
    每次请求时都会从Constance配置中获取最新的设置
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 每次请求时更新Admin站点设置
        if config:
            try:
                # 更新Admin站点标题
                admin.site.site_header = getattr(config, 'SITE_HEADER', '质量安全平台')
                admin.site.site_title = getattr(config, 'SITE_TITLE', '质量安全平台')
                admin.site.index_title = '系统管理'  # 固定为默认值
                
                # 更新SimpleUI Logo
                company_logo = getattr(config, 'COMPANY_LOGO', '')
                if company_logo:
                    settings.SIMPLEUI_LOGO = f'/media/{company_logo}'
                else:
                    settings.SIMPLEUI_LOGO = None
            except Exception:
                # 如果更新失败，保持默认设置
                pass
        
        response = self.get_response(request)
        return response
