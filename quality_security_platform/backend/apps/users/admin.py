from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'department', 'position', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'department', 'position')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'department')
    ordering = ('-created_at',)
    readonly_fields = ('last_login', 'date_joined', 'created_at', 'updated_at')
    fieldsets = (
        ('基础信息', {
            'fields': ('username', 'email', 'password', 'first_name', 'last_name', 'avatar', 'phone', 'department', 'position')
        }),
        ('权限设置', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('系统信息', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
