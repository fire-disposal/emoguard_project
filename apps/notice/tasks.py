"""
定时任务：情绪测评提醒 - 优化版
提升性能和健壮性，日志更完善
"""
from django.conf import settings
from celery import shared_task
# 推荐使用 celery.utils.log 来获取任务专用 logger
from celery.utils.log import get_task_logger 
from django.utils import timezone
from datetime import time, timedelta
# 导入 Q 对象用于更复杂的查询
from django.contrib.auth import get_user_model
from apps.emotiontracker.models import EmotionRecord
from apps.notice.services import send_template_msg
from typing import Literal

User = get_user_model()
# 使用任务专用的 logger
logger = get_task_logger(__name__) 

# 将时间切分点定义为常量，便于维护
MORNING_END_TIME = time(14, 0, 0) # 14:00:00

def get_time_range_for_period(today, period: Literal['morning', 'evening']):
    """
    根据日期和时间段获取查询情绪记录的精确时区时间范围。
    """
    tz = timezone.get_current_timezone()
    
    if period == "morning":
        # 早上：今天 00:00:00 到今天 14:00:00 (不包含)
        start = timezone.make_aware(timezone.datetime.combine(today, time.min), tz)
        end = timezone.make_aware(timezone.datetime.combine(today, MORNING_END_TIME), tz)
    elif period == "evening":
        # 晚上：今天 14:00:00 到明天 00:00:00 (不包含)
        start = timezone.make_aware(timezone.datetime.combine(today, MORNING_END_TIME), tz)
        tomorrow = today + timedelta(days=1)
        end = timezone.make_aware(timezone.datetime.combine(tomorrow, time.min), tz)
    else:
        # 兜底逻辑
        raise ValueError(f"无效的 period 参数: {period}")
        
    return start, end

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_mood_reminder(self, period: Literal['morning', 'evening'] = "morning"):
    """
    推送情绪测评提醒（period: 'morning'/'evening'）
    仅提醒有额度且未测评的用户，日志详细记录
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] 开始处理 {period} 情绪测评提醒任务.")
    
    now = timezone.localtime()
    today = now.date()
    template_id = settings.WECHAT_SUBSCRIPTION_TEMPLATES
    page_path = f"pages/mood/moodtest/moodtest?period={period}"
    thing = "早间情绪测评提醒" if period == "morning" else "晚间情绪测评提醒"
    
    start_time, end_time = get_time_range_for_period(today, period)

    # **性能优化：通过数据库查询排除已填写用户 (减少 Python 循环中的 DB 查询)**
    
    # 1. 过滤掉在指定时间段内已填写情绪记录的用户 ID
    filled_user_ids = EmotionRecord.objects.filter(
        created_at__gte=start_time,
        created_at__lt=end_time
    ).values_list('user_id', flat=True).distinct()

    # 2. 筛选需要提醒的用户: 
    #    - 排除已填写用户 ID
    #    - 考虑过滤有额度的用户 (如果启用)
    users_to_remind = User.objects.exclude(id__in=filled_user_ids)
    
    # 启用额度过滤 (如果需要，取消注释下面一行)
    users_to_remind = users_to_remind.filter(notice_quotas__count__gt=0).distinct()
    
    logger.info(f"[{task_id}] 共有 {users_to_remind.count()} 位用户需要发送 {period} 提醒.")

    successful_count = 0
    failed_count = 0
    
    for user in users_to_remind:
        try:
            # 内部业务逻辑（如：检查用户是否订阅、额度扣减等）应该在 send_template_msg 中处理
            result = send_template_msg(
                user=user,
                template_id=template_id,
                page_path=page_path,
                data_dict={
                    'thing1': {'value': thing},
                    'time2': {'value': now.strftime('%Y-%m-%d %H:%M')}
                }
            )
            
            # 记录成功日志
            logger.info(f"[{task_id}] 成功推送 {period} 提醒给 {user.username} (ID: {user.id})，结果: {result}")
            successful_count += 1
            
        except Exception as e:
            # 记录失败日志，包含任务 ID，便于回溯
            logger.error(
                f"[{task_id}] 推送 {period} 提醒给 {user.username} (ID: {user.id}) 失败: {e}",
                exc_info=True # 打印堆栈信息，提升健壮性
            )
            failed_count += 1
            
    logger.info(f"[{task_id}] {period} 情绪测评提醒任务完成. 成功: {successful_count}, 失败: {failed_count}.")