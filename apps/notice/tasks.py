"""
定时任务：情绪测评提醒
使用 Celery + django-celery-beat 实现
"""
from django.conf import settings
from celery import shared_task
from django.utils import timezone
from datetime import datetime, time, timedelta
from django.contrib.auth import get_user_model
from apps.emotiontracker.models import EmotionRecord
from apps.notice.services import send_template_msg

User = get_user_model()

def is_morning_filled(user, today):
    """判断用户今日早间是否已填写"""
    morning_end = datetime.combine(today, time(14, 0, 0, tzinfo=timezone.get_current_timezone()))
    return EmotionRecord.objects.filter(
        user_id=user.id,
        created_at__gte=datetime.combine(today, time(0, 0, 0, tzinfo=timezone.get_current_timezone())),
        created_at__lt=morning_end
    ).exists()

def is_evening_filled(user, today):
    """判断用户今日晚间是否已填写"""
    morning_end = datetime.combine(today, time(14, 0, 0, tzinfo=timezone.get_current_timezone()))
    return EmotionRecord.objects.filter(
        user_id=user.id,
        created_at__gte=morning_end,
        created_at__lt=datetime.combine(today + timedelta(days=1), time(0, 0, 0, tzinfo=timezone.get_current_timezone()))
    ).exists()

@shared_task
def send_morning_reminder():
    """
    早上 9:00 提醒用户进行早间情绪测评
    仅提醒有额度且今日早间未测评的用户
    """
    now = timezone.localtime()
    today = now.date()
    
    # 获取所有有额度的用户
    users_with_quota = User.objects.filter(
        notice_quotas__count__gt=0
    ).distinct()
    
    for user in users_with_quota:
        # 检查今日早间是否已填写
        if is_morning_filled(user, today):
            continue
            
        # 检查用户最后测评时间是否在今日早间之前
        if user.last_mood_tested_at:
            last_test_date = user.last_mood_tested_at.date()
            if last_test_date == today:
                last_test_time = user.last_mood_tested_at.time()
                if last_test_time < time(14, 0, 0):
                    continue
        
        # 发送提醒
        send_template_msg(
            user=user,
            template_id=settings.WECHAT_SUBSCRIPTION_TEMPLATES['MOOD_REMINDER'],
            page_path='pages/mood/moodtest/moodtest?period=morning',
            data_dict={
                'thing1': {'value': '早间情绪测评提醒'},
                'time2': {'value': now.strftime('%Y-%m-%d %H:%M')}
            }
        )

@shared_task
def send_evening_reminder():
    """
    晚上 21:00 提醒用户进行晚间情绪测评
    仅提醒有额度且今日晚间未测评的用户
    """
    now = timezone.localtime()
    today = now.date()
    
    # 获取所有有额度的用户
    users_with_quota = User.objects.filter(
        notice_quotas__count__gt=0
    ).distinct()
    
    for user in users_with_quota:
        # 检查今日晚间是否已填写
        if is_evening_filled(user, today):
            continue
            
        # 检查用户最后测评时间是否在今日晚间之前
        if user.last_mood_tested_at:
            last_test_date = user.last_mood_tested_at.date()
            if last_test_date == today:
                last_test_time = user.last_mood_tested_at.time()
                if last_test_time >= time(14, 0, 0):
                    continue
        
        # 发送提醒
        send_template_msg(
            user=user,
            template_id=settings.WECHAT_SUBSCRIPTION_TEMPLATES['MOOD_REMINDER'],
            page_path='pages/mood/moodtest/moodtest?period=evening',
            data_dict={
                'thing1': {'value': '晚间情绪测评提醒'},
                'time2': {'value': now.strftime('%Y-%m-%d %H:%M')}
            }
        )