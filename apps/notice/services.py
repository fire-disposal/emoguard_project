import requests
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from django.db.models import F
import logging
from .models import UserQuota, NotificationLog

logger = logging.getLogger("notice.services")

def get_wechat_access_token():
    """
    获取微信access_token
    """
    appid = settings.WECHAT_MINI_PROGRAM_APP_ID
    secret = settings.WECHAT_MINI_PROGRAM_APP_SECRET
    
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}"
    
    try:
        response = requests.get(url, timeout=5)
        result = response.json()
        return result.get('access_token')
    except Exception as e:
        logger.error(f"获取access_token失败: {e}")
        return None


def send_template_msg(user, template_id, page_path, data_dict):
    """
    发送模板消息的核心业务逻辑
    精简版：仅在出错或额度不足时打印日志
    """
    # 1. 检查并锁定额度
    try:
        with transaction.atomic():
            quota = UserQuota.objects.select_for_update().get(
                user=user,
                template_id=template_id,
                count__gt=0
            )
            # 正常流程日志已移除
    except UserQuota.DoesNotExist:
        NotificationLog.objects.create(
            user=user, template_id=template_id, message_data=data_dict,
            status='failed', error_response='无可用订阅额度'
        )
        logger.warning(f"推送失败: 用户 {user.username} 模板 {template_id} 无可用订阅额度")
        return False

    # 2. 获取Token
    access_token = get_wechat_access_token()
    if not access_token:
        NotificationLog.objects.create(
            user=user, template_id=template_id, message_data=data_dict,
            status='failed', error_response='无法获取access_token'
        )
        logger.error(f"用户 {user.username} 模板 {template_id} 获取access_token失败")
        return False

    # 3. 构造请求
    url = f"https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}"
    payload = {
        "touser": user.wechat_openid,
        "template_id": template_id,
        "page": page_path,
        "miniprogram_state": "formal",
        "lang": "zh_CN",
        "data": data_dict
    }

    # 4. 发送请求
    try:
        response = requests.post(url, json=payload, timeout=5)
        res_json = response.json()
    except Exception as e:
        NotificationLog.objects.create(
            user=user, template_id=template_id, message_data=data_dict,
            status='failed', error_response=str(e)
        )
        logger.error(f"用户 {user.username} 模板 {template_id} 微信接口异常: {e}")
        return False

    # 5. 处理结果
    if res_json.get('errcode') == 0:
        # 扣减额度
        quota.count = F('count') - 1
        quota.save()
        
        # 记录成功日志到数据库，但不打印控制台日志
        NotificationLog.objects.create(
            user=user, template_id=template_id, message_data=data_dict,
            status='success', wechat_msg_id=res_json.get('msgid'), sent_at=timezone.now()
        )
        return True
    else:
        # 记录失败
        NotificationLog.objects.create(
            user=user, template_id=template_id, message_data=data_dict,
            status='failed', error_response=res_json.get('errmsg')
        )
        logger.error(f"用户 {user.username} 模板 {template_id} 推送失败: {res_json.get('errmsg')}")
        return False