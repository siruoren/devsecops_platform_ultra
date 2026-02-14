from django.contrib import admin
from .models import Permission, Role, UserRole

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'module', 'is_menu', 'parent')
    search_fields = ('code', 'name', 'module')
    list_filter = ('module', 'is_menu', 'parent')
    ordering = ('module', 'code')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'description')
    search_fields = ('name', 'code', 'description')
    ordering = ('name',)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role', 'created_at')
    search_fields = ('user__username', 'role__name', 'role__code')
    list_filter = ('role',)
    ordering = ('-created_at',)
