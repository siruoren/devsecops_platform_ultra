from django.contrib import admin
from .models import Notification
from constance import config

# 设置站点标题（使用动态配置）
def get_admin_site_header():
    return getattr(config, 'SITE_HEADER', '质量安全平台')

def get_admin_site_title():
    return getattr(config, 'SITE_TITLE', '质量安全平台')

def get_admin_index_title():
    return getattr(config, 'INDEX_TITLE', '系统管理')

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
