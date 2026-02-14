import ldap
from django_auth_ldap.backend import LDAPBackend as BaseLDAPBackend
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType
from django.contrib.auth import get_user_model
from ..models import UnifiedAuthConfig

User = get_user_model()


class LDAPBackend(BaseLDAPBackend):
    """
    扩展 django-auth-ldap 的 LDAP 认证后端
    支持从系统配置动态读取 LDAP 配置
    """

    def __init__(self):
        super().__init__()
        self._load_config()

    def _load_config(self):
        """从数据库加载 LDAP 配置"""
        try:
            config = UnifiedAuthConfig.get_config()
            if not config.enabled or config.auth_type != 'ldap':
                return

            # 设置 LDAP 服务器 URI
            self.settings.SERVER_URI = config.ldap_server_uri

            # 设置绑定 DN 和密码
            if config.ldap_bind_dn and config.ldap_bind_password:
                self.settings.BIND_DN = config.ldap_bind_dn
                self.settings.BIND_PASSWORD = config.ldap_bind_password

            # 设置用户搜索
            if config.ldap_user_base_dn:
                self.settings.USER_SEARCH = LDAPSearch(
                    config.ldap_user_base_dn,
                    ldap.SCOPE_SUBTREE,
                    config.ldap_user_filter or '(uid=%(user)s)'
                )

            # 设置用户属性映射
            self.settings.USER_ATTR_MAP = {
                'username': 'uid',
                'email': 'mail',
                'first_name': 'givenName',
                'last_name': 'sn',
            }

            # 设置组同步
            if config.sync_groups and config.ldap_group_base_dn:
                self.settings.GROUP_SEARCH = LDAPSearch(
                    config.ldap_group_base_dn,
                    ldap.SCOPE_SUBTREE,
                    config.ldap_group_filter or '(objectClass=groupOfNames)'
                )
                self.settings.GROUP_TYPE = GroupOfNamesType()

            # 设置缓存
            self.settings.CACHE_TIMEOUT = 3600

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"加载 LDAP 配置失败: {e}")

    def get_or_create_user(self, username, ldap_user):
        """
        重写用户创建逻辑，支持自动创建用户
        """
        config = UnifiedAuthConfig.get_config()

        try:
            # 尝试获取现有用户
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            if not config.auto_create_user:
                return None

            # 创建新用户
            user = User(username=username)
            user.set_unusable_password()

        # 更新用户信息
        if config.update_user_info:
            for attr, value in ldap_user.attrs.items():
                if attr == 'mail' and value:
                    user.email = value[0] if isinstance(value, list) else value
                elif attr == 'givenName' and value:
                    user.first_name = value[0] if isinstance(value, list) else value
                elif attr == 'sn' and value:
                    user.last_name = value[0] if isinstance(value, list) else value

            user.save()

        return user