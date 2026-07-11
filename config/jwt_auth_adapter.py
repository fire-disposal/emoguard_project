"""
Django Ninja JWT 认证适配器
用于将django-ninja-jwt集成到现有的认证流程中
"""
import logging

from ninja_jwt.authentication import JWTAuth
from ninja_jwt.tokens import RefreshToken
from ninja_jwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import get_user_model

logger = logging.getLogger("django")

User = get_user_model()

jwt_auth = JWTAuth()

def create_tokens_for_user(user):
    """
    为用户创建访问令牌和刷新令牌
    适配django-ninja-jwt的令牌格式
    """
    refresh = RefreshToken.for_user(user)
    logger.info("[JWT] 签发令牌: user_id=%s", user.id)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def refresh_access_token(refresh_token_str):
    """使用刷新令牌换取新的访问令牌。

    启用 ROTATE_REFRESH_TOKENS + BLACKLIST_AFTER_ROTATION 后:
    - 校验旧 refresh;
    - 签发新 access;
    - 将旧 refresh 加入黑名单并签发新的 refresh(真轮换)。
    失败返回 None(旧令牌被拉黑或过期/无效)。
    """
    try:
        refresh = RefreshToken(refresh_token_str)
        access = str(refresh.access_token)

        new_refresh = refresh
        try:
            refresh.blacklist()
        except AttributeError:
            pass
        else:
            new_refresh = RefreshToken.for_user(
                User.objects.get(id=refresh["user_id"])
            )

        result = {"access": access, "refresh": str(new_refresh)}
        logger.info("[JWT] 刷新成功: user_id=%s", refresh.get("user_id", "?"))
        return result
    except (TokenError, InvalidToken, User.DoesNotExist) as e:
        logger.warning("[JWT] 刷新失败: %s", str(e))
        return None

def get_user_from_token(token_str):
    """从令牌字符串中获取用户"""
    try:
        refresh = RefreshToken(token_str)
        user_id = refresh['user_id']
        return User.objects.get(id=user_id)
    except (TokenError, InvalidToken, User.DoesNotExist) as e:
        logger.warning("[JWT] 令牌解析失败: %s", str(e))
        return None