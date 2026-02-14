from django.contrib.auth import get_user_model
from django_cas_ng.backends import CASBackend as BaseCASBackend
from ..models import UnifiedAuthConfig

User = get_user_model()


class CASBackend(BaseCASBackend):
    """
    CAS 认证后端
    基于 django-cas-ng 实现
    """

    def __init__(self):
        super().__init__()
        self._load_config()

    def _load_config(self):
        """加载 CAS 配置"""
        config = UnifiedAuthConfig.get_config()
        if not config.enabled or config.auth_type != 'cas':
            return

        # CAS 配置通过 settings.py 设置，或通过 Constance 动态设置
        from django.conf import settings
        if hasattr(settings, 'CAS_SERVER_URL'):
            # settings 中已有配置，使用之
            pass
        else:
            # 动态设置 settings（需要重启服务）
            import warnings
            warnings.warn("CAS 配置需要在 settings.py 中设置，动态配置暂不支持")

    def configure(self):
        """配置 CAS 客户端"""
        config = UnifiedAuthConfig.get_config()

        if config.cas_server_url:
            from django.conf import settings
            settings.CAS_SERVER_URL = config.cas_server_url
            settings.CAS_VERSION = config.cas_version or '3'
            settings.CAS_CREATE_USER = config.auto_create_user

    def get_user(self, user_id):
        """获取用户"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None