from django.contrib import admin
from apps.auth_unified.models import UnifiedAuthConfig


@admin.register(UnifiedAuthConfig)
class UnifiedAuthConfigAdmin(admin.ModelAdmin):
    fieldsets = (
        ('基础配置', {
            'fields': ('enabled', 'auth_type', 'auto_create_user', 'update_user_info', 'sync_groups')
        }),
        ('LDAP 配置', {
            'fields': ('ldap_server_uri', 'ldap_bind_dn', 'ldap_bind_password',
                       'ldap_user_base_dn', 'ldap_user_filter', 'ldap_group_base_dn', 'ldap_group_filter'),
            'classes': ('wide',),
            'description': '启用 LDAP 认证时需要配置以下字段'
        }),
        ('Keycloak/OIDC 配置', {
            'fields': ('oidc_server_url', 'oidc_realm', 'oidc_client_id', 'oidc_client_secret', 'oidc_public_key'),
            'classes': ('wide',),
            'description': '启用 Keycloak 认证时需要配置以下字段'
        }),
        ('CAS 配置', {
            'fields': ('cas_server_url', 'cas_version'),
            'classes': ('wide',),
            'description': '启用 CAS 认证时需要配置以下字段'
        }),
    )

    list_display = ('id', 'auth_type', 'enabled')