"""
微信认证服务
处理微信小程序登录相关功能
"""
import requests
import logging
from datetime import datetime
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import UserProfile

logger = logging.getLogger(__name__)
User = get_user_model()


class WeChatAuthService:
    """微信认证服务类"""
    
    def __init__(self):
        self.app_id = getattr(settings, 'WECHAT_MINI_PROGRAM_APP_ID', '')
        self.app_secret = getattr(settings, 'WECHAT_MINI_PROGRAM_APP_SECRET', '')
        
    def get_access_token(self, code):
        """
        使用微信登录凭证code获取session_key和openid
        
        Args:
            code: 微信登录凭证
            
        Returns:
            dict: 包含openid, session_key, unionid的字典
            
        Raises:
            Exception: 微信API调用失败
        """
        url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {
            'appid': self.app_id,
            'secret': self.app_secret,
            'js_code': code,
            'grant_type': 'authorization_code'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            result = response.json()
            
            if 'errcode' in result and result['errcode'] != 0:
                raise Exception(f"微信API错误: {result.get('errmsg', '未知错误')}")
            
            return {
                'openid': result.get('openid'),
                'session_key': result.get('session_key'),
                'unionid': result.get('unionid')
            }
        except requests.RequestException as e:
            logger.error(f"请求微信API失败: {str(e)}")
            raise Exception(f"请求微信API失败: {str(e)}")
    
    def decrypt_user_info(self, encrypted_data, iv, session_key):
        """
        解密微信用户信息
        
        Args:
            encrypted_data: 加密的数据
            iv: 初始向量
            session_key: 会话密钥
            
        Returns:
            dict: 解密后的用户信息
            
        Note:
            这里简化处理，实际项目中需要使用微信提供的解密算法
        """
        try:
            # TODO: 实现微信数据解密逻辑
            # 由于涉及加密算法，这里简化处理
            # 实际项目中需要使用微信提供的解密算法
            logger.warning("微信用户信息解密功能未实现，返回空数据")
            return {}
        except Exception as e:
            logger.error(f"解密用户信息失败: {str(e)}")
            return {}
    
    def get_or_create_user(self, openid, unionid=None, user_info=None):
        """
        根据openid获取或创建用户
        
        Args:
            openid: 微信openid
            unionid: 微信unionid（可选）
            user_info: 用户信息（可选）
            
        Returns:
            tuple: (user, created) 用户对象和是否创建的标志
        """
        try:
            user = User.objects.get(wechat_openid=openid)
            created = False
            logger.info(f"找到现有微信用户: {openid}")
        except User.DoesNotExist:
            user = User.objects.create_wechat_user(
                wechat_openid=openid,
                wechat_unionid=unionid
            )
            created = True
            logger.info(f"创建新微信用户: {openid}")
            
            # 创建用户资料
            if user_info:
                try:
                    UserProfile.objects.create(
                        user=user,
                        nickname=user_info.get('nickName', '微信用户'),
                        avatar=user_info.get('avatarUrl', ''),
                        gender=self._convert_gender(user_info.get('gender')),
                        bio=user_info.get('bio', '')
                    )
                    logger.info(f"为用户 {openid} 创建资料成功")
                except Exception as e:
                    logger.error(f"创建用户资料失败: {str(e)}")
        
        return user, created
    
    def _convert_gender(self, gender_value):
        """
        转换微信性别值到模型性别值
        
        Args:
            gender_value: 微信性别值 (1:男性, 2:女性)
            
        Returns:
            str: 模型性别值
        """
        if gender_value == 1:
            return 'male'
        elif gender_value == 2:
            return 'female'
        else:
            return 'other'
    
    def generate_tokens(self, user):
        """
        生成访问令牌和刷新令牌（已废弃）
        
        Note:
            此方法已废弃，请使用JWT认证适配器生成令牌
        """
        logger.warning("WeChatAuthService.generate_tokens 方法已废弃，请使用JWT认证适配器")
        # 这里简化处理，实际项目中应该使用JWT等标准方案
        access_token = f"access_{user.id}_{int(datetime.now().timestamp())}"
        refresh_token = f"refresh_{user.id}_{int(datetime.now().timestamp())}"
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': 7200  # 2小时
        }