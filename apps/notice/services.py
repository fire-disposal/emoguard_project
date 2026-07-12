import requests
from urllib.parse import urlencode
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from django.db.models import F
import logging
from .models import UserQuota, NotificationLog

logger = logging.getLogger("notice.services")

_WECHAT_TOKEN_CACHE_KEY = "wechat:access_token"


def get_wechat_access_token(force_refresh=False):
    """获取微信 access_token（缓存 ~7000s，复用现有 Redis，避免每次请求耗尽日配额）"""
    if not force_refresh:
        cached = cache.get(_WECHAT_TOKEN_CACHE_KEY)
        if cached:
            return cached

    appid = settings.WECHAT_MINI_PROGRAM_APP_ID
    secret = settings.WECHAT_MINI_PROGRAM_APP_SECRET
    params = urlencode({
        "grant_type": "client_credential",
        "appid": appid,
        "secret": secret,
    })
    url = f"https://api.weixin.qq.com/cgi-bin/token?{params}"

    try:
        response = requests.get(url, timeout=5)
        result = response.json()
    except Exception as e:
        # 不记录 url（含 secret），仅记录异常类型
        logger.error("获取access_token失败: %s", type(e).__name__)
        return None

    token = result.get('access_token')
    expires_in = result.get('expires_in', 7200)
    if token:
        cache.set(_WECHAT_TOKEN_CACHE_KEY, token, max(60, int(expires_in) - 200))
        return token

    logger.error("获取access_token失败: errcode=%s", result.get('errcode'))
    return None


def send_template_msg(user, template_id, page_path, data_dict):
    """发送订阅消息：原子扣减额度，发送失败则回补，token 过期重试一次"""
    if not user.wechat_openid:
        logger.warning("跳过推送: 用户 %s 无 wechat_openid", user.username)
        return False

    # 1. 原子条件扣减额度（immune to lost-update）
    rows = (
        UserQuota.objects
        .filter(user=user, template_id=template_id, count__gt=0)
        .update(count=F('count') - 1)
    )
    if rows == 0:
        NotificationLog.objects.create(
            user=user, template_id=template_id, message_data=data_dict,
            status='failed', error_response='无可用订阅额度'
        )
        return False

    def _refund():
        UserQuota.objects.filter(user=user, template_id=template_id).update(count=F('count') + 1)

    # 2. 获取 token
    access_token = get_wechat_access_token()
    if not access_token:
        _refund()
        NotificationLog.objects.create(
            user=user, template_id=template_id, message_data=data_dict,
            status='failed', error_response='无法获取access_token'
        )
        return False

    def _do_send(token):
        url = f"https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={token}"
        payload = {
            "touser": user.wechat_openid,
            "template_id": template_id,
            "page": page_path,
            "miniprogram_state": "formal",
            "lang": "zh_CN",
            "data": data_dict,
        }
        resp = requests.post(url, json=payload, timeout=5)
        return resp.json()

    # 3. 发送（token 失效 40001 时刷新重试一次）
    try:
        res_json = _do_send(access_token)
        if isinstance(res_json, dict) and res_json.get('errcode') == 40001:
            access_token = get_wechat_access_token(force_refresh=True)
            if access_token:
                res_json = _do_send(access_token)
    except Exception as e:
        _refund()
        NotificationLog.objects.create(
            user=user, template_id=template_id, message_data=data_dict,
            status='failed', error_response=str(e)
        )
        logger.error("用户 %s 模板 %s 微信接口异常: %s", user.username, template_id, type(e).__name__)
        return False

    # 4. 处理结果
    if not isinstance(res_json, dict):
        res_json = {}
    if res_json.get('errcode') == 0:
        NotificationLog.objects.create(
            user=user, template_id=template_id, message_data=data_dict,
            status='success', wechat_msg_id=res_json.get('msgid'), sent_at=timezone.now()
        )
        return True
    else:
        _refund()
        NotificationLog.objects.create(
            user=user, template_id=template_id, message_data=data_dict,
            status='failed', error_response=res_json.get('errmsg')
        )
        logger.error("用户 %s 模板 %s 推送失败: %s", user.username, template_id, res_json.get('errmsg'))
        return False
