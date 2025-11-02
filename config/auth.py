"""
认证和授权相关配置
统一使用django-ninja-jwt，删除旧的自定义JWT实现
"""
from django.contrib.auth import get_user_model

User = get_user_model()

def get_user_from_request(request):
    """
    从请求中获取当前用户
    使用django-ninja-jwt的认证机制
    """
    if hasattr(request, 'auth') and request.auth:
        return request.auth
    return None