"""
用户模块视图
提供用户管理、微信登录、用户资料管理等功能
"""
from ninja import Router, Query
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import UserProfile
from .serializers import (
    UserProfileCreateSchema, UserProfileUpdateSchema, UserProfileResponseSchema,
    UserResponseSchema, UserCreateSchema, AdminLoginSchema, AdminLoginResponseSchema,
    WeChatLoginSchema, WeChatLoginResponseSchema, UserListQuerySchema, 
    ProfileListQuerySchema, ErrorResponseSchema
)
from .wechat_auth import WeChatAuthService
from config.jwt_auth_adapter import jwt_auth, create_tokens_for_user
import logging

logger = logging.getLogger(__name__)

User = get_user_model()
users_router = Router(tags=['users'])
wechat_service = WeChatAuthService()


@users_router.post("/admin/login", response=AdminLoginResponseSchema)
def admin_login(request, data: AdminLoginSchema):
    """
    管理员账号密码登录
    仅支持login_type为password的用户
    """
    try:
        # 使用多认证后端进行认证
        user = authenticate(
            request=request,
            login_type='password',
            username=data.username,
            password=data.password
        )
        
        if not user:
            return ErrorResponseSchema(error="用户名或密码错误", detail="认证失败")
        
        # 检查是否为管理员
        if user.role != 'admin':
            return ErrorResponseSchema(error="权限不足", detail="该用户不是管理员")
        
        # 检查是否激活
        if not user.is_active:
            return ErrorResponseSchema(error="账户已禁用", detail="用户账户已禁用")
        
        # 生成JWT令牌
        tokens = create_tokens_for_user(user)
        
        logger.info(f"管理员 {data.username} 登录成功")
        
        return AdminLoginResponseSchema(
            access_token=tokens['access'],
            refresh_token=tokens['refresh'],
            user=UserResponseSchema(
                id=str(user.id),
                username=user.username,
                email=user.email,
                wechat_openid=user.wechat_openid,
                wechat_unionid=user.wechat_unionid,
                role=user.role,
                login_type=user.login_type,
                is_active=user.is_active,
                is_staff=user.is_staff,
                date_joined=user.date_joined.isoformat()
            )
        )
        
    except Exception as e:
        logger.error(f"管理员登录失败: {str(e)}")
        return ErrorResponseSchema(error="登录失败", detail=str(e))


@users_router.post("/admin/users", response=UserResponseSchema, auth=jwt_auth)
def create_user_by_admin(request, data: UserCreateSchema):
    """
    管理员创建用户
    只能创建login_type为password的用户
    """
    # 检查当前用户是否为管理员
    current_user = request.auth
    if current_user.role != 'admin':
        return ErrorResponseSchema(error="权限不足", detail="需要管理员权限")
    
    try:
        # 验证密码强度
        validate_password(data.password)
        
        # 创建用户
        user = User.objects.create_user(
            username=data.username,
            email=data.email,
            password=data.password,
            role=data.role,
            login_type='password'
        )
        
        logger.info(f"管理员 {current_user.username} 创建用户 {data.username}")
        
        return UserResponseSchema(
            id=str(user.id),
            username=user.username,
            email=user.email,
            wechat_openid=user.wechat_openid,
            wechat_unionid=user.wechat_unionid,
            role=user.role,
            login_type=user.login_type,
            is_active=user.is_active,
            is_staff=user.is_staff,
            date_joined=user.date_joined.isoformat()
        )
        
    except ValidationError as e:
        return ErrorResponseSchema(error="密码验证失败", detail=str(e))
    except Exception as e:
        logger.error(f"创建用户失败: {str(e)}")
        return ErrorResponseSchema(error="创建用户失败", detail=str(e))


@users_router.post("/wechat/login", response=WeChatLoginResponseSchema)
def wechat_login(request, data: WeChatLoginSchema):
    """
    微信小程序授权登录
    仅支持login_type为wechat的用户
    """
    try:
        # 使用code获取微信用户信息
        wechat_data = wechat_service.get_access_token(data.code)
        openid = wechat_data.get('openid')
        unionid = wechat_data.get('unionid')
        
        if not openid:
            return ErrorResponseSchema(error="微信登录失败", detail="无法获取openid")
        
        # 解密用户信息（如果有）
        user_info = None
        if data.encrypted_data and data.iv:
            user_info = wechat_service.decrypt_user_info(
                data.encrypted_data,
                data.iv,
                wechat_data.get('session_key')
            )
        
        # 获取或创建用户
        user, created = wechat_service.get_or_create_user(openid, unionid, user_info)
        
        # 生成JWT令牌
        tokens = create_tokens_for_user(user)
        
        # 获取用户资料
        profile = None
        try:
            profile_obj = UserProfile.objects.get(user=user)
            profile = UserProfileResponseSchema(
                id=profile_obj.id,
                user_id=str(user.id),
                nickname=profile_obj.nickname,
                avatar=profile_obj.avatar,
                gender=profile_obj.gender,
                birthday=profile_obj.birthday.isoformat() if profile_obj.birthday else None,
                bio=profile_obj.bio,
                phone=profile_obj.phone,
                address=profile_obj.address,
                created_at=profile_obj.created_at.isoformat(),
                updated_at=profile_obj.updated_at.isoformat()
            )
        except UserProfile.DoesNotExist:
            pass
        
        logger.info(f"微信用户 {openid} 登录成功，创建: {created}")
        
        return WeChatLoginResponseSchema(
            access_token=tokens['access'],
            refresh_token=tokens['refresh'],
            user=UserResponseSchema(
                id=str(user.id),
                username=user.username,
                email=user.email,
                wechat_openid=user.wechat_openid,
                wechat_unionid=user.wechat_unionid,
                role=user.role,
                login_type=user.login_type,
                is_active=user.is_active,
                is_staff=user.is_staff,
                date_joined=user.date_joined.isoformat()
            ),
            profile=profile
        )
        
    except Exception as e:
        logger.error(f"微信登录失败: {str(e)}")
        return ErrorResponseSchema(error="微信登录失败", detail=str(e))


@users_router.get("/profiles", response=list[UserProfileResponseSchema], auth=jwt_auth)
def list_profiles(request, filters: ProfileListQuerySchema = Query(...)):
    """
    获取用户资料列表，支持按用户ID过滤
    """
    queryset = UserProfile.objects.select_related('user')
    if filters.user_id:
        queryset = queryset.filter(user_id=filters.user_id)
    
    profiles = queryset.all()
    return [
        UserProfileResponseSchema(
            id=p.id,
            user_id=str(p.user_id),
            nickname=p.nickname,
            avatar=p.avatar,
            gender=p.gender,
            birthday=p.birthday.isoformat() if p.birthday else None,
            bio=p.bio,
            phone=p.phone,
            address=p.address,
            created_at=p.created_at.isoformat(),
            updated_at=p.updated_at.isoformat()
        )
        for p in profiles
    ]


@users_router.post("/profiles", response=UserProfileResponseSchema, auth=jwt_auth)
def create_profile(request, data: UserProfileCreateSchema):
    """
    创建用户资料
    """
    current_user = request.auth
    
    # 检查是否已存在资料
    if hasattr(current_user, 'profile'):
        return ErrorResponseSchema(error="资料已存在", detail="用户资料已存在，请使用更新接口")
    
    try:
        profile = UserProfile.objects.create(
            user=current_user,
            nickname=data.nickname,
            avatar=data.avatar,
            gender=data.gender,
            birthday=data.birthday,
            bio=data.bio,
            phone=data.phone,
            address=data.address
        )
        
        logger.info(f"用户 {current_user.username} 创建资料成功")
        
        return UserProfileResponseSchema(
            id=profile.id,
            user_id=str(current_user.id),
            nickname=profile.nickname,
            avatar=profile.avatar,
            gender=profile.gender,
            birthday=profile.birthday.isoformat() if profile.birthday else None,
            bio=profile.bio,
            phone=profile.phone,
            address=profile.address,
            created_at=profile.created_at.isoformat(),
            updated_at=profile.updated_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"创建用户资料失败: {str(e)}")
        return ErrorResponseSchema(error="创建用户资料失败", detail=str(e))


@users_router.put("/profiles/{profile_id}", response=UserProfileResponseSchema, auth=jwt_auth)
def update_profile(request, profile_id: int, data: UserProfileUpdateSchema):
    """
    更新用户资料
    """
    profile = get_object_or_404(UserProfile, id=profile_id)
    
    # 检查权限：只能更新自己的资料
    if profile.user != request.auth:
        return ErrorResponseSchema(error="权限不足", detail="只能更新自己的用户资料")
    
    # 更新字段
    update_fields = []
    if data.nickname is not None:
        profile.nickname = data.nickname
        update_fields.append('nickname')
    if data.avatar is not None:
        profile.avatar = data.avatar
        update_fields.append('avatar')
    if data.gender is not None:
        profile.gender = data.gender
        update_fields.append('gender')
    if data.birthday is not None:
        profile.birthday = data.birthday
        update_fields.append('birthday')
    if data.bio is not None:
        profile.bio = data.bio
        update_fields.append('bio')
    if data.phone is not None:
        profile.phone = data.phone
        update_fields.append('phone')
    if data.address is not None:
        profile.address = data.address
        update_fields.append('address')
    
    if update_fields:
        profile.save(update_fields=update_fields)
        logger.info(f"用户 {request.auth.username} 更新资料成功")
    
    return UserProfileResponseSchema(
        id=profile.id,
        user_id=str(profile.user_id),
        nickname=profile.nickname,
        avatar=profile.avatar,
        gender=profile.gender,
        birthday=profile.birthday.isoformat() if profile.birthday else None,
        bio=profile.bio,
        phone=profile.phone,
        address=profile.address,
        created_at=profile.created_at.isoformat(),
        updated_at=profile.updated_at.isoformat()
    )


@users_router.get("/users", response=list[UserResponseSchema], auth=jwt_auth)
def list_users(request, filters: UserListQuerySchema = Query(...)):
    """
    获取用户列表，支持按角色过滤
    """
    queryset = User.objects.all()
    if filters.role:
        queryset = queryset.filter(role=filters.role)
    
    users = queryset.all()
    return [
        UserResponseSchema(
            id=str(u.id),
            username=u.username,
            email=u.email,
            wechat_openid=u.wechat_openid,
            wechat_unionid=u.wechat_unionid,
            role=u.role,
            login_type=u.login_type,
            is_active=u.is_active,
            is_staff=u.is_staff,
            date_joined=u.date_joined.isoformat()
        )
        for u in users
    ]


@users_router.get("/users/{user_id}", response=UserResponseSchema, auth=jwt_auth)
def get_user(request, user_id: str):
    """
    获取单个用户信息
    """
    user = get_object_or_404(User, id=user_id)
    return UserResponseSchema(
        id=str(user.id),
        username=user.username,
        email=user.email,
        wechat_openid=user.wechat_openid,
        wechat_unionid=user.wechat_unionid,
        role=user.role,
        login_type=user.login_type,
        is_active=user.is_active,
        is_staff=user.is_staff,
        date_joined=user.date_joined.isoformat()
    )


@users_router.get("/me", response=dict, auth=jwt_auth)
def get_current_user(request):
    """
    获取当前登录用户信息
    """
    user = request.auth
    
    # 获取用户资料
    profile_data = None
    if hasattr(user, 'profile'):
        profile = user.profile
        profile_data = {
            "id": profile.id,
            "nickname": profile.nickname,
            "avatar": profile.avatar,
            "gender": profile.gender,
            "birthday": profile.birthday.isoformat() if profile.birthday else None,
            "bio": profile.bio,
            "phone": profile.phone,
            "address": profile.address,
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat()
        }
    
    return {
        "user": {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "wechat_openid": user.wechat_openid,
            "wechat_unionid": user.wechat_unionid,
            "role": user.role,
            "login_type": user.login_type,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "date_joined": user.date_joined.isoformat()
        },
        "profile": profile_data
    }
