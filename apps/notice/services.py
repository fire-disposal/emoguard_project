import requests
from django.utils import timezone
from django.conf import settings
from .models import UserQuota, NotificationLog


def get_wechat_access_token():
    """
    获取微信access_token
    这里需要根据你的微信配置实现具体的获取逻辑
    """
    appid = settings.WECHAT_APPID
    secret = settings.WECHAT_SECRET
    
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}"
    
    try:
        response = requests.get(url, timeout=5)
        result = response.json()
        return result.get('access_token')
    except Exception as e:
        print(f"获取access_token失败: {e}")
        return None


def send_template_msg(user, template_id, page_path, data_dict):
    """
    发送模板消息的核心业务逻辑
    :param user: User对象
    :param template_id: 微信模板ID
    :param page_path: 点击卡片跳转的小程序页面
    :param data_dict: 具体的字段内容 {'thing1': {'value': '...'}, ...}
    """
    
    # 1. 检查并扣除额度 (使用事务保证原子性)
    # 注意：必须先检查额度，因为如果没额度，微信接口会报错，且我们不需要发请求
    from django.db import transaction
    try:
        with transaction.atomic():
            quota = UserQuota.objects.select_for_update().get(
                user=user,
                template_id=template_id,
                count__gt=0
            )
    except UserQuota.DoesNotExist:
        # 记录一个失败日志，方便知道为什么没发
        NotificationLog.objects.create(
            user=user, template_id=template_id, message_data=data_dict,
            status='failed', error_response='无可用订阅额度'
        )
        return False

    # 2. 准备发送
    access_token = get_wechat_access_token()
    if not access_token:
        NotificationLog.objects.create(
            user=user, template_id=template_id, message_data=data_dict,
            status='failed', error_response='无法获取access_token'
        )
        return False
        
    url = f"https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}"
    
    payload = {
        "touser": user.openid,  # 确保你的User表里有openid字段
        "template_id": template_id,
        "page": page_path,
        "miniprogram_state": "formal",  # developer为开发版，formal为正式版
        "lang": "zh_CN",
        "data": data_dict
    }

    # 3. 调用微信接口
    try:
        response = requests.post(url, json=payload, timeout=5)
        res_json = response.json()
    except Exception as e:
        NotificationLog.objects.create(
            user=user, template_id=template_id, message_data=data_dict,
            status='failed', error_response=str(e)
        )
        return False

    # 4. 处理结果
    if res_json.get('errcode') == 0:
        # 发送成功：扣减额度，记录日志
        from django.db.models import F
        quota.count = F('count') - 1
        quota.save()
        
        NotificationLog.objects.create(
            user=user, template_id=template_id, message_data=data_dict,
            status='success', wechat_msg_id=res_json.get('msgid'), sent_at=timezone.now()
        )
        return True
    else:
        # 发送失败：额度不扣（或者根据策略扣除），记录错误
        # 常见错误：43101(用户拒绝接受消息)，40001(token过期)
        NotificationLog.objects.create(
            user=user, template_id=template_id, message_data=data_dict,
            status='failed', error_response=res_json.get('errmsg')
        )
        return False