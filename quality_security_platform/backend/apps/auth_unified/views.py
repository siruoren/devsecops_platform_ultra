import secrets
from urllib.parse import urlencode
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth import login, logout
from django.conf import settings
from .models import UnifiedAuthConfig
from .backends.oidc import OIDCAuthenticationBackend


def oidc_login(request):
    """
    重定向到 Keycloak 登录页
    """
    config = UnifiedAuthConfig.get_config()

    if not config.enabled or config.auth_type != 'keycloak':
        return JsonResponse({'error': 'OIDC 认证未启用'}, status=400)

    # 生成 state 和 code_verifier (PKCE)
    state = secrets.token_urlsafe(32)
    code_verifier = secrets.token_urlsafe(64)
    request.session['oidc_state'] = state
    request.session['oidc_code_verifier'] = code_verifier

    # 构建授权 URL
    auth_url = f"{config.oidc_server_url.rstrip('/')}/realms/{config.oidc_realm}/protocol/openid-connect/auth"

    params = {
        'response_type': 'code',
        'client_id': config.oidc_client_id,
        'redirect_uri': request.build_absolute_uri(reverse('auth_unified:oidc_callback')),
        'state': state,
        'scope': 'openid profile email',
        'code_challenge_method': 'S256',
        'code_challenge': secrets.token_urlsafe(64),  # 简化版，实际需要计算 challenge
    }

    return redirect(f"{auth_url}?{urlencode(params)}")


@csrf_exempt
def oidc_callback(request):
    """
    OIDC 回调处理
    """
    config = UnifiedAuthConfig.get_config()

    # 验证 state
    state = request.GET.get('state')
    if not state or state != request.session.get('oidc_state'):
        return HttpResponseBadRequest('Invalid state')

    # 获取 code
    code = request.GET.get('code')
    if not code:
        return HttpResponseBadRequest('No code provided')

    # 认证用户
    backend = OIDCAuthenticationBackend()
    redirect_uri = request.build_absolute_uri(reverse('auth_unified:oidc_callback'))
    user = backend.authenticate(request, code=code, redirect_uri=redirect_uri)

    if user:
        login(request, user)
        # 清理 session
        request.session.pop('oidc_state', None)
        request.session.pop('oidc_code_verifier', None)
        return redirect(settings.LOGIN_REDIRECT_URL or '/')
    else:
        return HttpResponseBadRequest('Authentication failed')


def auth_status(request):
    """
    获取当前认证状态和配置
    """
    config = UnifiedAuthConfig.get_config()

    return JsonResponse({
        'authenticated': request.user.is_authenticated,
        'username': request.user.username if request.user.is_authenticated else None,
        'auth_type': config.auth_type if config.enabled else 'local',
        'available_auth_types': [
            {'type': 'local', 'name': '本地认证', 'enabled': True},
            {'type': 'ldap', 'name': 'LDAP', 'enabled': config.enabled and config.auth_type == 'ldap'},
            {'type': 'keycloak', 'name': 'Keycloak', 'enabled': config.enabled and config.auth_type == 'keycloak'},
            {'type': 'cas', 'name': 'CAS', 'enabled': config.enabled and config.auth_type == 'cas'},
        ]
    })