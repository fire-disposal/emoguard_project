"""
用户模块视图 - 适配单模型设计
提供用户管理、微信登录、用户资料管理等功能
"""

from ninja import Router
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import logging

from .serializers import (
    UserProfileUpdateSchema,
    UserResponseSchema,
    UserCreateSchema,
    AdminLoginSchema,
    AdminLoginResponseSchema,
    WeChatLoginSchema,
    WeChatLoginResponseSchema,
)
from .wechat_auth import WeChatAuthService
from .rate_limit import wechat_login_rate_limit, admin_login_rate_limit
from config.jwt_auth_adapter import jwt_auth, create_tokens_for_user

logger = logging.getLogger(__name__)

User = get_user_model()
users_router = Router(tags=["users"])
wechat_service = WeChatAuthService()


def _user_to_response_schema(user):
    """将User对象转换为UserResponseSchema"""
    return UserResponseSchema(
        id=str(user.id),
        username=user.username,
        email=user.email,
        wechat_openid=user.wechat_openid,
        wechat_unionid=user.wechat_unionid,
        role=user.role,
        is_active=user.is_active,
        is_staff=user.is_staff,
        nickname=user.nickname,
        real_name=user.real_name,
        avatar=user.avatar,
        gender=user.gender,
        birthday=user.birthday,
        bio=user.bio,
        phone=user.phone,
        address=user.address,
        education=user.education,
        occupation=user.occupation,
    )


@users_router.post("/admin/login", response=AdminLoginResponseSchema)
@admin_login_rate_limit
def admin_login(request, data: AdminLoginSchema):
    """管理员账号密码登录"""
    username = data.username.strip()
    
    user = authenticate(
        request=request,
        username=username,
        password=data.password,
    )
    
    if not user:
        logger.warning(f"管理员登录失败: 用户名={username[:3]}***")
        raise HttpError(401, "用户名或密码错误")
    
    if user.role != "admin":
        logger.warning(f"非管理员尝试登录管理员界面: {username}")
        raise HttpError(403, "该用户不是管理员")
    
    if not user.is_active:
        logger.warning(f"已禁用的管理员尝试登录: {username}")
        raise HttpError(403, "账户已禁用")
    
    tokens = create_tokens_for_user(user)
    logger.info(f"管理员 {username} 登录成功")
    
    return AdminLoginResponseSchema(
        access_token=tokens["access"],
        refresh_token=tokens["refresh"],
        user=_user_to_response_schema(user),
    )


@users_router.post("/admin/users", response=UserResponseSchema, auth=jwt_auth)
def create_user_by_admin(request, data: UserCreateSchema):
    """管理员创建用户"""
    current_user = request.auth
    if current_user.role != "admin":
        logger.warning(f"非管理员尝试创建用户: {current_user.username}")
        raise HttpError(403, "需要管理员权限")
    
    username = data.username.strip()
    email = data.email.strip() if data.email else None
    
    try:
        validate_password(data.password)
    except ValidationError as e:
        raise HttpError(400, str(e))
    
    if User.objects.filter(username=username).exists():
        raise HttpError(400, "用户名已存在")
    
    if email and User.objects.filter(email=email).exists():
        raise HttpError(400, "邮箱已被使用")
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=data.password,
        role=data.role,
    )
    
    logger.info(f"管理员 {current_user.username} 创建用户成功: {username}")
    return _user_to_response_schema(user)


@users_router.post("/wechat/login", response=WeChatLoginResponseSchema)
@wechat_login_rate_limit
def wechat_login(request, data: WeChatLoginSchema):
    """微信小程序授权登录"""
    if not data.code or len(data.code.strip()) == 0:
        raise HttpError(400, "微信登录凭证不能为空")
    
    if len(data.code) != 32:
        raise HttpError(400, "无效的微信登录凭证格式")
    
    wechat_data = wechat_service.get_access_token(data.code)
    openid = wechat_data.get("openid")
    unionid = wechat_data.get("unionid")
    session_key = wechat_data.get("session_key")
    
    if not openid:
        logger.error(f"微信API未返回openid，响应数据: {wechat_data}")
        raise HttpError(500, "无法获取微信用户信息")
    
    user_info = None
    if data.encrypted_data and data.iv and session_key:
        try:
            user_info = wechat_service.decrypt_user_info(
                data.encrypted_data, data.iv, session_key
            )
            logger.info(f"用户信息解密成功: {user_info.get('nickName', '未知用户')}")
        except Exception as e:
            logger.warning(f"用户信息解密失败: {str(e)}，继续使用基础登录")
    
    user, created = wechat_service.get_or_create_user(openid, unionid, user_info)
    
    if not user.is_active:
        logger.warning(f"用户账户已禁用: {openid}")
        raise HttpError(403, "用户账户已禁用")
    
    tokens = create_tokens_for_user(user)
    logger.info(f"微信用户 {openid[:8]}... 登录成功，新用户: {created}")
    
    return WeChatLoginResponseSchema(
        access_token=tokens["access"],
        refresh_token=tokens["refresh"],
        user=_user_to_response_schema(user),
    )


@users_router.put("/me/profile", response=UserResponseSchema, auth=jwt_auth)
def update_my_profile(request, data: UserProfileUpdateSchema):
    """更新当前用户资料"""
    user = request.auth
    
    update_fields = []
    for field in ['nickname', 'real_name', 'avatar', 'gender', 'birthday', 'bio', 
                  'phone', 'address', 'education', 'occupation']:
        value = getattr(data, field, None)
        if value is not None:
            setattr(user, field, value)
            update_fields.append(field)
    
    if update_fields:
        user.save(update_fields=update_fields)
        logger.info(f"用户 {user.username} 更新资料成功: {update_fields}")
    
    return _user_to_response_schema(user)


@users_router.get("/users", response=list[UserResponseSchema], auth=jwt_auth)
def list_users(request, role=None):
    """获取用户列表，支持按角色过滤"""
    queryset = User.objects.all()
    if role:
        queryset = queryset.filter(role=role)
    
    return [_user_to_response_schema(u) for u in queryset]


@users_router.get("/users/{user_id}", response=UserResponseSchema, auth=jwt_auth)
def get_user(request, user_id):
    """获取单个用户信息"""
    user = get_object_or_404(User, id=user_id)
    return _user_to_response_schema(user)


@users_router.get("/me", response=UserResponseSchema, auth=jwt_auth)
def get_current_user(request):
    """获取当前登录用户完整信息"""
    return _user_to_response_schema(request.auth)
