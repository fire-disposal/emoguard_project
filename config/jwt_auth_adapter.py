"""
Django Ninja JWT 认证适配器
用于将django-ninja-jwt集成到现有的认证流程中
"""
import logging
logger = logging.getLogger("django")
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.tokens import RefreshToken
from ninja_jwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import get_user_model

User = get_user_model()

# 创建全局JWT认证实例
jwt_auth = JWTAuth()

def create_tokens_for_user(user):
    """
    为用户创建访问令牌和刷新令牌
    适配django-ninja-jwt的令牌格式
    """
    refresh = RefreshToken.for_user(user)
    logger.info(f"[JWT] 创建令牌: 用户ID={user.id}, refresh={str(refresh)}, access={str(refresh.access_token)}")
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def refresh_access_token(refresh_token_str):
    """
    使用刷新令牌获取新的访问令牌
    """
    try:
        logger.info(f"[JWT] 刷新令牌请求: refresh_token_str={refresh_token_str}")
        refresh = RefreshToken(refresh_token_str)
        result = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),  # 返回新的刷新令牌
        }
        logger.info(f"[JWT] 刷新令牌成功: 新access={result['access']}, 新refresh={result['refresh']}")
        return result
    except (TokenError, InvalidToken) as e:
        logger.error(f"[JWT] 刷新令牌失败: {str(e)}")
        return None

def get_user_from_token(token_str):
    """
    从令牌字符串中获取用户
    """
    try:
        logger.info(f"[JWT] 解析令牌: token_str={token_str}")
        refresh = RefreshToken(token_str)
        user_id = refresh['user_id']
        logger.info(f"[JWT] 令牌解析成功: user_id={user_id}")
        return User.objects.get(id=user_id)
    except (TokenError, InvalidToken, User.DoesNotExist) as e:
        logger.error(f"[JWT] 令牌解析失败: {str(e)}")
        return None