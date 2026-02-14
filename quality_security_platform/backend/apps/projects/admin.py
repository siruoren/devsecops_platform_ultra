from django.contrib import admin
from .models import Project, Environment, ServerIP


class ServerIPInline(admin.TabularInline):
    model = ServerIP
    extra = 1
    fields = ('ip',)
    verbose_name = '服务器IP'
    verbose_name_plural = '服务器IP列表'


@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_server_ips', 'created_at')
    search_fields = ('name',)
    inlines = [ServerIPInline]
    
    def get_server_ips(self, obj):
        return ', '.join([server_ip.ip for server_ip in obj.server_ips.all()])
    get_server_ips.short_description = '服务器IP'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'git_repo', 'environment', 'owner', 'created_at')
    search_fields = ('name', 'git_repo')
    list_filter = ('environment', 'owner')
    
    def save_model(self, request, obj, form, change):
        if not change and not obj.owner:
            obj.owner = request.user
        super().save_model(request, obj, form, change)
