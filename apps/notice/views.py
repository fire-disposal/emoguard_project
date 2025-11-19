from ninja import Router
from django.db.models import F
from .models import UserQuota
from .serializers import SubscribeSyncSchema, UserQuotaSchema, SubscribeSyncResponseSchema
from config.jwt_auth_adapter import jwt_auth

notice_router = Router(tags=["notice"])

@notice_router.get("/notice/quota", response=list[UserQuotaSchema], auth=jwt_auth)
def get_user_quota(request):
    """
    查询接口：前端在渲染页面时调用，判断是否需要弹窗
    """
    quotas = UserQuota.objects.filter(user=request.user, count__gt=0)
    return [UserQuotaSchema(template_id=q.template_id, count=q.count) for q in quotas]

@notice_router.post("/notice/subscribe", response=SubscribeSyncResponseSchema, auth=jwt_auth)
def sync_subscribe(request, data: SubscribeSyncSchema):
    """
    同步接口：前端 wx.requestSubscribeMessage 回调成功后调用
    """
    template_id = data.template_id
    action = data.action

    if action == 'accept':
        quota, created = UserQuota.objects.get_or_create(
            user=request.user,
            template_id=template_id
        )
        quota.count = F('count') + 1
        quota.save()
        return SubscribeSyncResponseSchema(status="success", msg="订阅次数已增加")
    return SubscribeSyncResponseSchema(status="ignored", msg="用户拒绝或被封禁")