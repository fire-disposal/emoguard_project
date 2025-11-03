"""
请求频率限制装饰器
为微信登录和管理员登录提供频率限制保护
"""
import logging
from functools import wraps
from django.core.cache import cache
from django.conf import settings
from ninja.errors import HttpError

logger = logging.getLogger(__name__)


def rate_limit(key_prefix, max_requests=5, window_seconds=60):
    """
    简单的频率限制装饰器
    
    Args:
        key_prefix: 缓存键前缀
        max_requests: 最大请求次数
        window_seconds: 时间窗口（秒）
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # 获取客户端IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            # 构造缓存键
            cache_key = f"rate_limit:{key_prefix}:{ip}"
            
            # 获取当前计数
            current = cache.get(cache_key, 0)
            
            if current >= max_requests:
                logger.warning(f"频率限制触发: {ip} -> {key_prefix}")
                raise HttpError(429, "请求过于频繁，请稍后重试")
            
            # 增加计数
            cache.set(cache_key, current + 1, window_seconds)
            
            return view_func(request, *args, **kwargs)
        
        return wrapped_view
    return decorator


# 预定义的频率限制装饰器
wechat_login_rate_limit = rate_limit(
    key_prefix='wechat_login',
    max_requests=getattr(settings, 'WECHAT_LOGIN_RATE_LIMIT_COUNT', 10),
    window_seconds=getattr(settings, 'WECHAT_LOGIN_RATE_LIMIT_WINDOW', 60)
)

admin_login_rate_limit = rate_limit(
    key_prefix='admin_login',
    max_requests=getattr(settings, 'ADMIN_LOGIN_RATE_LIMIT_COUNT', 5),
    window_seconds=getattr(settings, 'ADMIN_LOGIN_RATE_LIMIT_WINDOW', 60)
)