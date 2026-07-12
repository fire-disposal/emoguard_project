"""
微信认证服务
处理微信小程序登录相关功能
"""
import requests
import logging
import base64
import json
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
        验证微信登录凭证code是否已使用（原子 SET NX 防并发重放）

        Args:
            code: 微信登录凭证

        Raises:
            Exception: code已使用或无效
        """
        cache_key = f"wechat_code_{code}"
        # cache.add 在 Redis 上是原子 SET NX；返回 False 表示 key 已存在（已用过）
        if not cache.add(cache_key, True, 300):
            raise Exception("微信登录凭证已使用")
        logger.info("微信code验证通过: %s...", code[:10])

    def get_or_create_user(self, openid, unionid=None, user_info=None):
        """
        根据openid获取或创建用户（并发安全）

        Args:
            openid: 微信openid
            unionid: 微信unionid（可选）
            user_info: 用户信息（可选）

        Returns:
            tuple: (user, created) 用户对象和是否创建的标志
        """
        gender = ''
        if user_info:
            gender = self._convert_gender(user_info.get('gender'))

        with transaction.atomic():
            user, created = User.objects.get_or_create(
                wechat_openid=openid,
                defaults={
                    'username': openid,
                    'wechat_unionid': unionid,
                    'role': 'user',
                    'gender': gender,
                },
            )
            if created:
                user.set_unusable_password()
                user.save(update_fields=['password'])
                logger.info("创建新微信用户: %s", openid)
                return user, True

        # 已存在：按需更新 unionid / gender
        update_fields = []
        if unionid and user.wechat_unionid != unionid:
            user.wechat_unionid = unionid
            update_fields.append('wechat_unionid')
        if user_info and not user.gender and user_info.get('gender'):
            user.gender = self._convert_gender(user_info.get('gender'))
            update_fields.append('gender')
        if update_fields:
            user.save(update_fields=update_fields)
            logger.info("更新用户信息: %s, 字段: %s", openid, update_fields)
        return user, False

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
            return ''  # 返回空字符串而不是'other'，避免null值
    