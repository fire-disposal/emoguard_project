"""
用户服务 - 统一处理用户相关操作
"""
from typing import Optional, Dict
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class UserService:
    """用户服务类 - 处理所有用户相关操作"""
    
    @staticmethod
    def get_user_profile(user_id: str) -> Optional[Dict]:
        """
        获取用户资料
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户资料字典或None
        """
        try:
            user = User.objects.get(id=user_id)
            return {
                'education': getattr(user, 'education', None),
                'age': getattr(user, 'age', None),
                'gender': getattr(user, 'gender', None),
            }
        except ObjectDoesNotExist:
            logger.warning(f"用户 {user_id} 不存在")
            return None
        except Exception as e:
            logger.error(f"获取用户资料失败: {str(e)}")
            return None
    
    @staticmethod
    def update_cognitive_assessment_status(user_id: str) -> bool:
        """
        更新用户认知评估完成状态
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否成功更新
        """
        try:
            user = User.objects.get(id=user_id)
            if hasattr(user, 'has_completed_cognitive_assessment'):
                if not user.has_completed_cognitive_assessment:
                    user.has_completed_cognitive_assessment = True
                    user.save(update_fields=['has_completed_cognitive_assessment'])
                    return True
            return False
        except ObjectDoesNotExist:
            logger.warning(f"更新认知评估状态时用户 {user_id} 不存在")
            return False
        except Exception as e:
            logger.error(f"更新认知评估状态失败: {str(e)}")
            return False
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[User]:
        """
        根据ID获取用户对象
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户对象或None
        """
        try:
            return User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            logger.warning(f"用户 {user_id} 不存在")
            return None
        except Exception as e:
            logger.error(f"获取用户对象失败: {str(e)}")
            return None