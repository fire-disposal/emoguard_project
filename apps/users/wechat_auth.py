"""
微信认证服务
处理微信小程序登录相关功能
"""
import requests
import logging
import base64
import json
from typing import Optional, Tuple, Dict, Any
from Crypto.Cipher import AES
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.cache import cache

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
            encrypted_data: 加密的数据 (Base64编码)
            iv: 初始向量 (Base64编码)
            session_key: 会话密钥 (Base64编码)
            
        Returns:
            dict: 解密后的用户信息
            
        Raises:
            Exception: 解密失败
        """
        try:
            # Base64解码
            encrypted_data_bytes = base64.b64decode(encrypted_data)
            iv_bytes = base64.b64decode(iv)
            session_key_bytes = base64.b64decode(session_key)
            
            # AES-128-CBC解密
            cipher = AES.new(session_key_bytes, AES.MODE_CBC, iv_bytes)
            decrypted = cipher.decrypt(encrypted_data_bytes)
            
            # 去除PKCS#7填充
            pad = decrypted[-1]
            if pad < 1 or pad > 32:
                raise ValueError("无效的填充")
            
            decrypted = decrypted[:-pad]
            
            # 解析JSON数据
            user_info = json.loads(decrypted.decode('utf-8'))
            
            # 验证数据水印
            watermark = user_info.get('watermark', {})
            appid = watermark.get('appid')
            
            if appid != self.app_id:
                raise ValueError(f"AppID不匹配: 期望 {self.app_id}, 实际 {appid}")
            
            logger.info(f"微信用户信息解密成功: {user_info.get('nickName', '未知用户')}")
            return user_info
            
        except json.JSONDecodeError as e:
            logger.error(f"解析用户信息JSON失败: {str(e)}")
            raise Exception("用户信息格式错误")
        except ValueError as e:
            logger.error(f"数据验证失败: {str(e)}")
            raise Exception("用户信息验证失败")
        except Exception as e:
            logger.error(f"解密用户信息失败: {str(e)}")
            raise Exception("用户信息解密失败")
    
    def validate_wechat_code(self, code):
        """
        验证微信登录凭证code是否已使用
        
        Args:
            code: 微信登录凭证
            
        Raises:
            Exception: code已使用或无效
        """
        cache_key = f"wechat_code_{code}"
        if cache.get(cache_key):
            raise Exception("微信登录凭证已使用")
        # 设置5分钟有效期，防止重放攻击
        cache.set(cache_key, True, 300)
        logger.info(f"微信code验证通过: {code[:10]}...")

    def get_or_create_user(self, openid, unionid=None, user_info=None):
        """
        根据openid获取或创建用户 - 单模型设计
        
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
            
            # 更新unionid（如果提供且不同）
            update_fields = []
            if unionid and user.wechat_unionid != unionid:
                user.wechat_unionid = unionid
                update_fields.append('wechat_unionid')
            
            # 更新用户资料（如果提供且相关字段为空）
            if user_info:
                if not user.nickname and user_info.get('nickName'):
                    user.nickname = self._clean_nickname(user_info.get('nickName'))
                    update_fields.append('nickname')
                if not user.avatar and user_info.get('avatarUrl'):
                    user.avatar = self._validate_avatar(user_info.get('avatarUrl'))
                    update_fields.append('avatar')
                if not user.gender and user_info.get('gender'):
                    user.gender = self._convert_gender(user_info.get('gender'))
                    update_fields.append('gender')
            
            if update_fields:
                user.save(update_fields=update_fields)
                logger.info(f"更新用户信息: {openid}, 字段: {update_fields}")
                
        except User.DoesNotExist:
            # 创建新用户,使用事务确保数据一致性
            with transaction.atomic():  # type: ignore[misc]
                # 准备用户资料
                nickname = ''
                avatar = None
                gender = None
                
                if user_info:
                    nickname = self._clean_nickname(user_info.get('nickName', ''))
                    avatar = self._validate_avatar(user_info.get('avatarUrl', ''))
                    gender = self._convert_gender(user_info.get('gender'))
                
                # 创建用户，直接包含资料字段
                user = User.objects.create(
                    username=openid,
                    wechat_openid=openid,
                    wechat_unionid=unionid,
                    role='user',
                    nickname=nickname,
                    avatar=avatar,
                    gender=gender,
                )
                user.set_unusable_password()
                user.save()
                
                created = True
                logger.info(f"创建新微信用户: {openid}")
        
        return user, created

    def _clean_nickname(self, nickname):
        """
        清理和验证昵称
        
        Args:
            nickname: 原始昵称
            
        Returns:
            str: 清理后的昵称
        """
        # 简单的昵称清理逻辑
        if not nickname or not nickname.strip():
            return '微信用户'
        
        # 移除特殊字符，保留中文、字母、数字、常用符号
        import re
        cleaned = re.sub(r'[^\w\u4e00-\u9fff\s\-_.]', '', nickname)
        
        # 限制长度
        if len(cleaned) > 30:
            cleaned = cleaned[:30]
        
        return cleaned.strip() or '微信用户'

    def _validate_avatar(self, avatar_url):
        """
        验证头像URL
        
        Args:
            avatar_url: 头像URL
            
        Returns:
            str: 验证后的URL或None
        """
        if not avatar_url:
            return None
            
        # 验证URL格式
        from urllib.parse import urlparse
        try:
            result = urlparse(avatar_url)
            if not all([result.scheme, result.netloc]):
                return None
                
            # 验证域名（微信头像域名）
            allowed_domains = ['wx.qlogo.cn', 'thirdwx.qlogo.cn']
            if result.netloc not in allowed_domains:
                logger.warning(f"非微信官方头像域名: {result.netloc}")
                return None
                
            return avatar_url
            
        except Exception as e:
            logger.error(f"头像URL验证失败: {str(e)}")
            return None

    def _convert_gender(self, gender_value):
        """
        转换微信性别值到模型性别值 - 增强验证
        
        Args:
            gender_value: 微信性别值 (1:男性, 2:女性, 0:未知)
            
        Returns:
            str: 模型性别值
        """
        if gender_value == 1:
            return 'male'
        elif gender_value == 2:
            return 'female'
        else:
            return 'other'  # 包括未知和其他情况
    