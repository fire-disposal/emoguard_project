"""
认证后端
统一处理密码认证和微信认证
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class MultiAuthBackend(ModelBackend):
    """
    统一认证后端
    支持密码认证和微信认证
    """
    
    def authenticate(self, request, username=None, password=None, wechat_openid=None, **kwargs):
        """统一认证入口"""
        if wechat_openid:
            return self._authenticate_wechat(wechat_openid)
        if username and password:
            return self._authenticate_password(username, password)
        return None
    
    def _authenticate_password(self, username, password):
        """密码认证"""
        try:
            # 支持邮箱或用户名登录
            user = User.objects.get(email=username) if '@' in username else User.objects.get(username=username)
            
            # 确保用户有密码
            if user.has_usable_password() and user.check_password(password):
                logger.info(f"密码认证成功: {username}")
                return user
        except User.DoesNotExist:
            logger.warning(f"用户不存在: {username}")
        return None
    
    def _authenticate_wechat(self, wechat_openid):
        """微信认证"""
        try:
            user = User.objects.get(wechat_openid=wechat_openid)
            logger.info(f"微信认证成功: {wechat_openid[:8]}...")
            return user
        except User.DoesNotExist:
            logger.warning(f"微信用户不存在: {wechat_openid[:8]}...")
        return None