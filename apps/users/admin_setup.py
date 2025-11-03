"""
管理员账户自动创建
系统启动时自动创建默认管理员
"""
import os
from django.contrib.auth import get_user_model
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


def create_default_admin():
    """创建默认管理员账户"""
    try:
        # 检查是否已有管理员
        if User.objects.filter(is_superuser=True).exists():
            logger.info("管理员已存在，跳过创建")
            return
        
        # 从环境变量读取配置
        username = os.environ.get('DEFAULT_ADMIN_USERNAME', 'admin')
        email = os.environ.get('DEFAULT_ADMIN_EMAIL', 'admin@emoguard.com')
        password = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'admin123456')
        
        # 创建管理员
        User.objects.create_superuser(username=username, email=email, password=password)
        
        logger.info(f"默认管理员创建成功: {username}")
        logger.warning(f"默认密码: {password} - 请及时修改！")
        
    except IntegrityError as e:
        logger.error(f"创建管理员失败: {e}")
    except Exception as e:
        logger.error(f"创建管理员异常: {e}")


def ensure_admin_exists():
    """确保系统有管理员"""
    try:
        if not User.objects.filter(is_superuser=True).exists():
            logger.warning("系统无管理员，正在创建...")
            create_default_admin()
        else:
            logger.debug("管理员已存在")
    except Exception as e:
        logger.error(f"检查管理员异常: {e}")