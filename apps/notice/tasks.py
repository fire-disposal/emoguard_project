"""
定时任务：情绪测评提醒 - 轻量版
移除 Celery，直接同步调用
"""
from django.conf import settings
from django.utils import timezone
from datetime import time, timedelta
import logging
from django.contrib.auth import get_user_model
from apps.emotiontracker.models import EmotionRecord
from apps.notice.services import send_template_msg
from typing import Literal

User = get_user_model()
logger = logging.getLogger(__name__)

MORNING_END_TIME = time(14, 0, 0)


def get_time_range_for_period(today, period: Literal['morning', 'evening']):
    tz = timezone.get_current_timezone()
    if period == "morning":
        start = timezone.make_aware(timezone.datetime.combine(today, time.min), tz)
        end = timezone.make_aware(timezone.datetime.combine(today, MORNING_END_TIME), tz)
    elif period == "evening":
        start = timezone.make_aware(timezone.datetime.combine(today, MORNING_END_TIME), tz)
        tomorrow = today + timedelta(days=1)
        end = timezone.make_aware(timezone.datetime.combine(tomorrow, time.min), tz)
    else:
        raise ValueError(f"无效的 period 参数: {period}")
    return start, end


def send_mood_reminder(period: Literal['morning', 'evening'] = "morning"):
    """
    推送情绪测评提醒（period: 'morning'/'evening'）
    仅提醒有额度且未测评的用户
    """
    logger.info(f"开始处理 {period} 情绪测评提醒任务.")

    now = timezone.localtime()
    today = now.date()
    template_id = settings.WECHAT_SUBSCRIPTION_TEMPLATES
    page_path = f"pages/mood/moodtest/moodtest?period={period}"
    thing = "早间情绪测评提醒" if period == "morning" else "晚间情绪测评提醒"

    start_time, end_time = get_time_range_for_period(today, period)

    filled_user_ids = EmotionRecord.objects.filter(
        created_at__gte=start_time,
        created_at__lt=end_time
    ).values_list('user_id', flat=True).distinct()

    users_to_remind = User.objects.exclude(id__in=filled_user_ids)
    users_to_remind = users_to_remind.filter(notice_quotas__count__gt=0).distinct()

    logger.info(f"共有 {users_to_remind.count()} 位用户需要发送 {period} 提醒.")

    successful_count = 0
    failed_count = 0

    for user in users_to_remind:
        try:
            result = send_template_msg(
                user=user,
                template_id=template_id,
                page_path=page_path,
                data_dict={
                    'thing1': {'value': thing},
                    'time2': {'value': now.strftime('%Y-%m-%d %H:%M')}
                }
            )
            logger.info(f"成功推送 {period} 提醒给 {user.username} (ID: {user.id}), 结果: {result}")
            successful_count += 1
        except Exception as e:
            logger.error(
                f"推送 {period} 提醒给 {user.username} (ID: {user.id}) 失败: {e}",
                exc_info=True
            )
            failed_count += 1

    logger.info(f"{period} 情绪测评提醒任务完成. 成功: {successful_count}, 失败: {failed_count}.")
