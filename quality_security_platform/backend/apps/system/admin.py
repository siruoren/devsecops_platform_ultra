from django.contrib import admin
from .models import Notification

# 设置站点标题
admin.site.site_header = '质量安全平台'  # 登录页面标题
admin.site.site_title = '质量安全平台'    # 浏览器标签标题
admin.site.index_title = '系统管理'      # 首页标题

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'sender', 'title', 'is_read', 'created_at', 'read_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('title', 'content', 'recipient__username', 'sender__username')
    readonly_fields = ('created_at', 'read_at')
    ordering = ('-created_at',)
    
    def save_model(self, request, obj, form, change):
        if not change and not obj.sender:
            obj.sender = request.user
        super().save_model(request, obj, form, change)
