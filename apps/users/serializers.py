from ninja import Schema
from typing import Optional
from datetime import datetime


class UserProfileCreateSchema(Schema):
    """创建用户资料"""
    nickname: str
    avatar: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class UserProfileUpdateSchema(Schema):
    """更新用户资料"""
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class UserProfileResponseSchema(Schema):
    """用户资料响应"""
    id: int
    user_id: str
    nickname: str
    avatar: Optional[str]
    gender: Optional[str]
    birthday: Optional[str]
    bio: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    created_at: str
    updated_at: str


class UserResponseSchema(Schema):
    """用户响应"""
    id: str
    username: str
    email: Optional[str]
    wechat_openid: Optional[str]
    wechat_unionid: Optional[str]
    role: str
    login_type: str
    is_active: bool
    is_staff: bool
    date_joined: str


class UserCreateSchema(Schema):
    """创建用户（管理员功能）"""
    username: str
    email: Optional[str] = None
    password: str
    role: str = "user"


class AdminLoginSchema(Schema):
    """管理员登录"""
    username: str  # 可以是邮箱或用户名
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
    profile: Optional[UserProfileResponseSchema] = None


class UserListQuerySchema(Schema):
    """用户列表查询参数"""
    role: Optional[str] = None


class ProfileListQuerySchema(Schema):
    """用户资料列表查询参数"""
    user_id: Optional[str] = None


class ErrorResponseSchema(Schema):
    """错误响应"""
    error: str
    detail: Optional[str] = None
    timestamp: str = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()