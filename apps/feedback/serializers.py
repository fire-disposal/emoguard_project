"""用户反馈序列化器 - 简化版本"""
from ninja import Schema, Field
from typing import Optional


class FeedbackCreateSchema(Schema):
    """创建反馈的序列化器 - 最简版本"""
    rating: int = Field(ge=1, le=5)  # 评分 1-5
    content: Optional[str] = Field(default=None, max_length=500)  # 反馈内容，最多500字


class FeedbackResponseSchema(Schema):
    """反馈响应序列化器"""
    id: int
    rating: int
    content: str
    is_processed: bool
    created_at: str  # ISO格式时间字符串


class FeedbackListResponseSchema(Schema):
    """反馈列表响应序列化器 - 精简版"""
    id: int
    rating: int
    content: str
    user_display_name: Optional[str]  # 用户显示名称
    is_processed: bool
    created_at: str