from ninja import Schema
from typing import Optional, List


class SubscribeSyncSchema(Schema):
    """用于接收前端传来的订阅结果"""
    template_id: str
    action: str  # choices: ['accept', 'reject', 'ban']


class UserQuotaSchema(Schema):
    """用于返回当前额度"""
    template_id: str
    count: int


class UserQuotaListSchema(Schema):
    """用户额度列表响应"""
    quotas: List[UserQuotaSchema]


class SubscribeSyncResponseSchema(Schema):
    """订阅同步响应"""
    status: str
    msg: str


class NotificationLogSchema(Schema):
    """通知日志响应"""
    id: int
    user_id: str
    template_id: str
    message_data: dict
    assessment_id: Optional[int] = None
    status: str
    wechat_msg_id: Optional[str] = None
    error_response: Optional[str] = None
    created_at: str
    sent_at: Optional[str] = None


class NotificationLogListSchema(Schema):
    """通知日志列表响应"""
    logs: List[NotificationLogSchema]
    total: int
    page: int
    page_size: int


class NotificationLogQuerySchema(Schema):
    """通知日志查询参数"""
    template_id: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    page: int = 1
    page_size: int = 10


class SendTemplateMessageSchema(Schema):
    """发送模板消息请求"""
    template_id: str
    page_path: str
    data_dict: dict
    assessment_id: Optional[int] = None


class SendTemplateMessageResponseSchema(Schema):
    """发送模板消息响应"""
    success: bool
    message: str
    log_id: Optional[int] = None