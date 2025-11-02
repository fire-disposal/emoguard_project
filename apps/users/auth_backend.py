"""
多认证后端支持
支持传统账号密码登录和微信小程序登录
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    邮箱/用户名 + 密码认证后端
    用于管理员和传统用户登录
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        使用邮箱或用户名进行认证
        """
        if not username or not password:
            return None
        
        try:
            # 尝试通过邮箱查找用户
            if '@' in username:
                user = User.objects.get(email=username, login_type='password')
            else:
                # 尝试通过用户名查找用户
                user = User.objects.get(username=username, login_type='password')
            
            # 检查密码
            if user.check_password(password):
                logger.info(f"用户 {username} 通过密码认证成功")
                return user
            
        except User.DoesNotExist:
            logger.warning(f"用户 {username} 不存在或不是密码用户")
            return None
        
        return None
    
    def get_user(self, user_id):
        """
        根据用户ID获取用户
        """
        try:
            return User.objects.get(pk=user_id, login_type='password')
        except User.DoesNotExist:
            return None


class WeChatBackend(ModelBackend):
    """
    微信小程序认证后端
    用于微信小程序用户登录
    """
    
    def authenticate(self, request, wechat_openid=None, **kwargs):
        """
        使用微信openid进行认证
        """
        if not wechat_openid:
            return None
        
        try:
            user = User.objects.get(
                wechat_openid=wechat_openid, 
                login_type='wechat'
            )
            logger.info(f"微信用户 {wechat_openid} 认证成功")
            return user
            
        except User.DoesNotExist:
            logger.warning(f"微信用户 {wechat_openid} 不存在")
            return None
    
    def get_user(self, user_id):
        """
        根据用户ID获取用户
        """
        try:
            return User.objects.get(pk=user_id, login_type='wechat')
        except User.DoesNotExist:
            return None


class MultiAuthBackend(ModelBackend):
    """
    统一认证后端
    根据登录类型自动选择认证方式
    """
    
    def authenticate(self, request, login_type=None, **credentials):
        """
        统一认证入口
        """
        if login_type == 'password':
            # 传统账号密码登录
            username = credentials.get('username')
            password = credentials.get('password')
            return EmailBackend().authenticate(request, username, password)
        
        elif login_type == 'wechat':
            # 微信小程序登录
            wechat_openid = credentials.get('wechat_openid')
            return WeChatBackend().authenticate(request, wechat_openid)
        
        else:
            # 默认使用传统认证
            username = credentials.get('username')
            password = credentials.get('password')
            return EmailBackend().authenticate(request, username, password)
    
    def get_user(self, user_id):
        """
        根据用户ID获取用户
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None