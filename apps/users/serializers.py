from ninja import Schema
from typing import Optional
from datetime import date


class UserProfileUpdateSchema(Schema):
    """更新用户资料（现在直接更新User模型）"""
    nickname: Optional[str] = None
    real_name: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[date] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    education: Optional[str] = None
    occupation: Optional[str] = None


class UserResponseSchema(Schema):
    """用户响应 - 包含所有字段"""
    id: str
    username: str
    email: Optional[str] = None
    
    # 微信字段
    wechat_openid: Optional[str] = None
    wechat_unionid: Optional[str] = None
    
    # 角色与权限
    role: str
    is_active: bool
    is_staff: bool
    
    # 用户资料字段
    nickname: str
    real_name: str
    avatar: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[date] = None
    bio: str
    phone: Optional[str] = None
    address: str
    education: Optional[str] = None
    occupation: str


class UserCreateSchema(Schema):
    """创建用户（管理员功能）"""
    username: str
    email: Optional[str] = None
    password: str
    role: str = "user"


class AdminLoginSchema(Schema):
    """管理员登录"""
    username: str
    password: str


class AdminLoginResponseSchema(Schema):
    """管理员登录响应"""
    access_token: str
    refresh_token: str
    user: UserResponseSchema


class WeChatLoginSchema(Schema):
    """微信小程序登录"""
    code: str
    encrypted_data: Optional[str] = None
    iv: Optional[str] = None


class WeChatLoginResponseSchema(Schema):
    """微信登录响应"""
    access_token: str
    refresh_token: str
    user: UserResponseSchema