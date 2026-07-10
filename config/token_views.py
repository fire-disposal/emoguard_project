"""令牌刷新视图（带尾斜杠，适配小程序 /api/token/refresh/）。

背景：django-ninja-jwt 的 NinjaJWTDefaultController 注册的是无尾斜杠路由
（/api/token/refresh），而小程序与 RefreshTokenRateLimitMiddleware 均按带尾
斜杠路径（/api/token/refresh/）约定。历史实现错位导致小程序刷新令牌请求 404。

此视图仅补齐带尾斜杠入口，复用 config.jwt_auth_adapter.refresh_access_token，
不改动小程序、不触碰 ninja 控制器内部。请求/响应契约与小程序一致：
    请求  POST JSON  {"refresh": "<refresh_token>"}
    成功  200  {"access": "<new_access>", "refresh": "<new_refresh>"}
    失败  401  {"detail": "令牌无效或已过期", "code": "token_not_valid"}
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from config.jwt_auth_adapter import refresh_access_token

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def token_refresh_slash(request):
    """带尾斜杠的令牌刷新端点。限流由 RefreshTokenRateLimitMiddleware 处理。"""
    try:
        body = json.loads(request.body.decode("utf-8")) if request.body else {}
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"detail": "无法解析请求体"}, status=400)

    refresh_str = body.get("refresh")
    if not refresh_str:
        return JsonResponse({"detail": "缺少 refresh 字段"}, status=400)

    result = refresh_access_token(refresh_str)
    if result is None:
        return JsonResponse(
            {"detail": "令牌无效或已过期", "code": "token_not_valid"},
            status=401,
        )

    return JsonResponse(result, status=200)
