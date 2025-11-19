from ninja import Schema
from typing import Optional



class UserProfileUpdateSchema(Schema):
    """更新用户资料（现在直接更新User模型）"""
    real_name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    education: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    phone: Optional[str] = None


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
    real_name: str
    gender: Optional[str] = None
    age: Optional[int] = None
    education: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    phone: Optional[str] = None
    is_profile_complete: bool
    
    # 评估状态
    has_completed_cognitive_assessment: bool

    # 测评分数字段
    score_scd: Optional[float] = None
    score_mmse: Optional[float] = None
    score_moca: Optional[float] = None
    score_gad7: Optional[float] = None
    score_phq9: Optional[float] = None
    score_adl: Optional[float] = None
    # 新增：上次每日情绪测试时间
    last_mood_tested_at: Optional[str] = None

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