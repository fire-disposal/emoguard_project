"""
用户输入验证器
使用Django原生验证功能
"""
import re
from django.core.validators import validate_email as django_validate_email
from django.core.exceptions import ValidationError


def validate_phone(phone):
    """
    验证手机号
    
    Args:
        phone: 手机号
        
    Returns:
        str: 验证后的手机号或None
        
    Raises:
        ValidationError: 验证失败
    """
    if not phone:
        return None
    
    # 中国手机号正则表达式
    phone_pattern = r'^1[3-9]\d{9}$'
    if not re.match(phone_pattern, phone):
        raise ValidationError("无效的手机号格式")
    
    return phone


def sanitize_text(text, max_length=None):
    """
    清理输入文本
    
    Args:
        text: 输入文本
        max_length: 最大长度
        
    Returns:
        str: 清理后的文本
    """
    if not text:
        return ""
    
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 限制长度
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()