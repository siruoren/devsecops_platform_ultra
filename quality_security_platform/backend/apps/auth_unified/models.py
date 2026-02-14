from django.db import models
from django.conf import settings
from constance import config


class UnifiedAuthConfig(models.Model):
    """统一认证配置（单例模式）"""
    AUTH_TYPES = (
        ('local', '本地认证'),
        ('ldap', 'LDAP'),
        ('keycloak', 'Keycloak (OIDC)'),
        ('cas', 'CAS'),
    )

    enabled = models.BooleanField('启用统一认证', default=False)
    auth_type = models.CharField('认证类型', max_length=20, choices=AUTH_TYPES, default='local')

    # LDAP 配置
    ldap_server_uri = models.CharField('LDAP服务器地址', max_length=255, blank=True)
    ldap_bind_dn = models.CharField('LDAP绑定DN', max_length=255, blank=True)
    ldap_bind_password = models.CharField('LDAP绑定密码', max_length=255, blank=True)
    ldap_user_base_dn = models.CharField('用户基础DN', max_length=255, blank=True)
    ldap_user_filter = models.CharField('用户过滤器', max_length=255, default='(uid=%(user)s)', blank=True)
    ldap_group_base_dn = models.CharField('组基础DN', max_length=255, blank=True)
    ldap_group_filter = models.CharField('组过滤器', max_length=255, blank=True)

    # Keycloak/OIDC 配置
    oidc_server_url = models.CharField('OIDC服务器地址', max_length=255, blank=True)
    oidc_realm = models.CharField('Realm名称', max_length=100, blank=True)
    oidc_client_id = models.CharField('Client ID', max_length=100, blank=True)
    oidc_client_secret = models.CharField('Client Secret', max_length=255, blank=True)
    oidc_public_key = models.TextField('OIDC公钥', blank=True)

    # CAS 配置
    cas_server_url = models.CharField('CAS服务器地址', max_length=255, blank=True)
    cas_version = models.CharField('CAS版本', max_length=10, default='3', blank=True)

    # 通用配置
    auto_create_user = models.BooleanField('自动创建用户', default=True)
    update_user_info = models.BooleanField('每次登录更新用户信息', default=True)
    sync_groups = models.BooleanField('同步用户组', default=False)

    class Meta:
        db_table = 'auth_unified_config'
        verbose_name = '统一认证配置'

    @classmethod
    def get_config(cls):
        """获取单例配置"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj