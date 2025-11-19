from ninja import Schema


class UserQuotaSchema(Schema):
    """用户订阅额度响应"""
    template_id: str
    count: int


class SubscribeSyncSchema(Schema):
    """订阅同步请求"""
    template_id: str
    action: str  # choices: ['accept', 'reject', 'ban']


class SubscribeSyncResponseSchema(Schema):
    """订阅同步响应"""
    status: str
    msg: str
