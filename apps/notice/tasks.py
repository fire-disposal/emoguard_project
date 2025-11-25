"""
定时任务：情绪测评提醒
只保留一种推送逻辑，提升健壮性，日志更完善
"""
from django.conf import settings
from celery import shared_task
from django.utils import timezone
from datetime import datetime, time, timedelta
from django.contrib.auth import get_user_model
from apps.emotiontracker.models import EmotionRecord
from apps.notice.services import send_template_msg
import logging

User = get_user_model()
logger = logging.getLogger("notice.tasks")

def is_mood_filled(user, today, period):
    """判断用户今日是否已填写情绪测评（period: morning/evening）"""
    tz = timezone.get_current_timezone()
    if period == "morning":
        start = datetime.combine(today, time(0, 0, 0, tzinfo=tz))
        end = datetime.combine(today, time(14, 0, 0, tzinfo=tz))
    else:
        start = datetime.combine(today, time(14, 0, 0, tzinfo=tz))
        end = datetime.combine(today + timedelta(days=1), time(0, 0, 0, tzinfo=tz))
    return EmotionRecord.objects.filter(
        user_id=user.id,
        created_at__gte=start,
        created_at__lt=end
    ).exists()

@shared_task
def send_mood_reminder(period="morning"):
    """
    推送情绪测评提醒（period: morning/evening）
    仅提醒有额度且未测评的用户，日志详细记录
    """
    now = timezone.localtime()
    today = now.date()
    template_id = settings.WECHAT_SUBSCRIPTION_TEMPLATES
    page_path = f"pages/mood/moodtest/moodtest?period={period}"
    thing = "早间情绪测评提醒" if period == "morning" else "晚间情绪测评提醒"

    users_with_quota = User.objects.filter(
        notice_quotas__count__gt=0
    ).distinct()

    for user in users_with_quota:
        try:
            if is_mood_filled(user, today, period):
                logger.info(f"{user.username} 已填写 {period} 测评，跳过")
                continue

            # 可根据 period 判断 last_mood_tested_at 是否需要跳过
            if user.last_mood_tested_at:
                last_test_date = user.last_mood_tested_at.date()
                last_test_time = user.last_mood_tested_at.time()
                if last_test_date == today:
                    if period == "morning" and last_test_time < time(14, 0, 0):
                        logger.info(f"{user.username} 今日早间已测评，跳过")
                        continue
                    if period == "evening" and last_test_time >= time(14, 0, 0):
                        logger.info(f"{user.username} 今日晚间已测评，跳过")
                        continue

            # 发送提醒
            result = send_template_msg(
                user=user,
                template_id=template_id,
                page_path=page_path,
                data_dict={
                    'thing1': {'value': thing},
                    'time2': {'value': now.strftime('%Y-%m-%d %H:%M')}
                }
            )
            logger.info(f"推送 {period} 测评提醒给 {user.username}，结果: {result}")
        except Exception as e:
            logger.error(f"推送 {period} 测评提醒给 {user.username} 失败: {e}")
