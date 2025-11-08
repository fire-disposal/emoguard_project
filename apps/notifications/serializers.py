"""
通知系统序列化器
"""
from ninja import Schema
from typing import Optional
from datetime import datetime


class NotificationSchema(Schema):
    """通知响应Schema"""
    id: int
    title: str
    content: str
    notification_type: str
    is_read: bool
    related_id: Optional[int] = None
    related_type: Optional[str] = None
    created_at: datetime
    read_at: Optional[datetime] = None


class NotificationCreateSchema(Schema):
    """创建通知Schema（管理员使用）"""
    title: str
    content: str
    notification_type: str = 'system'
    related_id: Optional[int] = None
    related_type: Optional[str] = None
    # 注意：管理员创建通知时，user_id应该从请求参数或路由参数获取，而不是从JWT


class UnreadCountSchema(Schema):
    """未读数量Schema"""
    count: int
