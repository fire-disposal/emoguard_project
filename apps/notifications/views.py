"""
通知系统视图
提供通知的CRUD操作
"""
from ninja import Router
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from typing import List
import logging

from .models import Notification
from .serializers import NotificationSchema, NotificationCreateSchema, UnreadCountSchema
from config.jwt_auth_adapter import jwt_auth
from config.schemas import create_paginated_response

logger = logging.getLogger(__name__)
User = get_user_model()

notifications_router = Router(tags=["notifications"])


@notifications_router.get("/", response=dict, auth=jwt_auth)
def list_notifications(request, page: int = 1, page_size: int = 20, is_read: bool = None):
    """
    获取当前用户的通知列表
    支持分页和按已读状态过滤
    """
    user = request.auth
    queryset = Notification.objects.filter(user=user)
    
    # 过滤已读状态
    if is_read is not None:
        queryset = queryset.filter(is_read=is_read)
    
    # 计算分页
    total = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size
    
    notifications = queryset[start:end]
    
    # 序列化数据
    items = [
        NotificationSchema(
            id=n.id,
            title=n.title,
            content=n.content,
            notification_type=n.notification_type,
            is_read=n.is_read,
            related_id=n.related_id,
            related_type=n.related_type,
            created_at=n.created_at,
            read_at=n.read_at
        ).dict()
        for n in notifications
    ]
    
    return create_paginated_response(items, total, page, page_size)


@notifications_router.get("/{notification_id}", response=NotificationSchema, auth=jwt_auth)
def get_notification(request, notification_id: int):
    """获取单个通知详情"""
    user = request.auth
    notification = get_object_or_404(Notification, id=notification_id, user=user)
    
    return NotificationSchema(
        id=notification.id,
        title=notification.title,
        content=notification.content,
        notification_type=notification.notification_type,
        is_read=notification.is_read,
        related_id=notification.related_id,
        related_type=notification.related_type,
        created_at=notification.created_at,
        read_at=notification.read_at
    )


@notifications_router.put("/{notification_id}/read", response=NotificationSchema, auth=jwt_auth)
def mark_notification_as_read(request, notification_id: int):
    """标记通知为已读"""
    user = request.auth
    notification = get_object_or_404(Notification, id=notification_id, user=user)
    
    notification.mark_as_read()
    logger.info(f"用户 {user.username} 标记通知 {notification_id} 为已读")
    
    return NotificationSchema(
        id=notification.id,
        title=notification.title,
        content=notification.content,
        notification_type=notification.notification_type,
        is_read=notification.is_read,
        related_id=notification.related_id,
        related_type=notification.related_type,
        created_at=notification.created_at,
        read_at=notification.read_at
    )


@notifications_router.delete("/{notification_id}", auth=jwt_auth)
def delete_notification(request, notification_id: int):
    """删除通知"""
    user = request.auth
    notification = get_object_or_404(Notification, id=notification_id, user=user)
    
    notification.delete()
    logger.info(f"用户 {user.username} 删除通知 {notification_id}")
    
    return {"message": "删除成功"}


@notifications_router.get("/unread-count", response=UnreadCountSchema, auth=jwt_auth)
def get_unread_count(request):
    """获取未读通知数量"""
    user = request.auth
    count = Notification.objects.filter(user=user, is_read=False).count()
    
    return UnreadCountSchema(count=count)


@notifications_router.post("/", response=NotificationSchema, auth=jwt_auth)
def create_notification(request, data: NotificationCreateSchema):
    """
    创建通知（管理员功能）
    """
    current_user = request.auth
    
    # 仅管理员可创建通知
    if current_user.role != 'admin':
        raise HttpError(403, "需要管理员权限")
    
    # 获取目标用户
    target_user = get_object_or_404(User, id=data.user_id)
    
    # 创建通知
    notification = Notification.objects.create(
        user=target_user,
        title=data.title,
        content=data.content,
        notification_type=data.notification_type,
        related_id=data.related_id,
        related_type=data.related_type
    )
    
    logger.info(f"管理员 {current_user.username} 创建通知给用户 {target_user.username}")
    
    return NotificationSchema(
        id=notification.id,
        title=notification.title,
        content=notification.content,
        notification_type=notification.notification_type,
        is_read=notification.is_read,
        related_id=notification.related_id,
        related_type=notification.related_type,
        created_at=notification.created_at,
        read_at=notification.read_at
    )
