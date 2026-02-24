from django.contrib import admin
from .models import Notification, SystemConfig

# 设置站点标题（从数据库中读取配置）
def get_admin_site_header():
    try:
        config = SystemConfig.objects.filter(key='SITE_HEADER').first()
        return config.value if config else '质量安全平台'
    except Exception:
        return '质量安全平台'

def get_admin_site_title():
    try:
        config = SystemConfig.objects.filter(key='SITE_TITLE').first()
        return config.value if config else '质量安全平台'
    except Exception:
        return '质量安全平台'

def get_admin_index_title():
    try:
        config = SystemConfig.objects.filter(key='INDEX_TITLE').first()
        return config.value if config else '系统管理'
    except Exception:
        return '系统管理'

# 设置站点标题
admin.site.site_header = get_admin_site_header()  # 登录页面标题
admin.site.site_title = get_admin_site_title()    # 浏览器标签标题
admin.site.index_title = get_admin_index_title()      # 首页标题

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('title', 'content', 'user__username')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
