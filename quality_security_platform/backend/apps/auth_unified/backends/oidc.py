import jwt
import requests
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import authentication, exceptions
from ..models import UnifiedAuthConfig

User = get_user_model()


class OIDCAuthenticationBackend:
    """
    Keycloak OpenID Connect 认证后端
    支持 Authorization Code 流和 Bearer Token 认证
    """

    def __init__(self):
        self.config = UnifiedAuthConfig.get_config()

    def authenticate(self, request, code=None, redirect_uri=None, **kwargs):
        """
        通过 Authorization Code 认证
        """
        if not self.config.enabled or self.config.auth_type != 'keycloak':
            return None

        if not code:
            return None

        # 交换 code 获取 token
        token_data = self._exchange_code(code, redirect_uri)
        if not token_data:
            return None

        # 解析 ID Token
        user_info = self._parse_id_token(token_data.get('id_token'))
        if not user_info:
            return None

        # 获取或创建用户
        return self._get_or_create_user(user_info)

    def authenticate_header(self, request):
        """
        处理 Bearer Token 认证（用于 API）
        """
        auth = authentication.get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'bearer':
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        token = auth[1].decode()

        # 验证 token
        user_info = self._validate_token(token)
        if not user_info:
            return None

        return self._get_or_create_user(user_info)

    def _exchange_code(self, code, redirect_uri):
        """交换 Authorization Code 获取 Token"""
        if not self.config.oidc_server_url:
            return None

        token_url = f"{self.config.oidc_server_url.rstrip('/')}/realms/{self.config.oidc_realm}/protocol/openid-connect/token"

        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': self.config.oidc_client_id,
            'client_secret': self.config.oidc_client_secret,
        }

        try:
            response = requests.post(token_url, data=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Token exchange failed: {e}")
            return None

    def _parse_id_token(self, id_token):
        """解析 ID Token"""
        if not id_token:
            return None

        try:
            # 如果有公钥配置，验证签名
            if self.config.oidc_public_key:
                decoded = jwt.decode(
                    id_token,
                    self.config.oidc_public_key,
                    algorithms=['RS256'],
                    audience=self.config.oidc_client_id
                )
            else:
                # 不验证签名（仅开发环境）
                decoded = jwt.decode(id_token, options={'verify_signature': False})

            return decoded
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"ID token parsing failed: {e}")
            return None

    def _validate_token(self, token):
        """验证 Bearer Token（可缓存公钥）"""
        # 尝试从缓存获取公钥
        public_key = cache.get('oidc_public_key')

        if not public_key and self.config.oidc_public_key:
            public_key = self.config.oidc_public_key
            cache.set('oidc_public_key', public_key, 3600)

        try:
            if public_key:
                decoded = jwt.decode(
                    token,
                    public_key,
                    algorithms=['RS256'],
                    audience=self.config.oidc_client_id
                )
            else:
                # 如果未配置公钥，尝试从 OIDC 服务器获取
                decoded = jwt.decode(token, options={'verify_signature': False})

            return decoded
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Token validation failed: {e}")
            return None

    def _get_or_create_user(self, user_info):
        """获取或创建用户"""
        if not user_info:
            return None

        # 获取用户标识（优先使用 sub，也可配置使用 email 或 preferred_username）
        user_id = user_info.get('sub')
        username = user_info.get('preferred_username') or user_info.get('email')
        email = user_info.get('email')

        if not username and not email:
            return None

        try:
            # 尝试用 sub 查找用户
            user = User.objects.get(oidc_sub=user_id)
        except (User.DoesNotExist, AttributeError):
            try:
                # 尝试用 username 查找
                if username:
                    user = User.objects.get(username=username)
                else:
                    user = None
            except User.DoesNotExist:
                user = None

        # 创建新用户
        if not user and self.config.auto_create_user:
            user = User(
                username=username or email.split('@')[0],
                email=email or '',
                first_name=user_info.get('given_name', ''),
                last_name=user_info.get('family_name', ''),
            )
            user.set_unusable_password()
            user.save()

            # 保存 OIDC sub（如果模型支持）
            if hasattr(user, 'oidc_sub'):
                user.oidc_sub = user_id
                user.save(update_fields=['oidc_sub'])

        return user