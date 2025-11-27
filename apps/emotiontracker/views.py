from ninja import Router
from django.utils import timezone
from datetime import time
from .models import EmotionRecord
from .serializers import (
    EmotionRecordCreateSchema, EmotionRecordResponseSchema
)
from config.jwt_auth_adapter import jwt_auth

emotion_router = Router(tags=["emotiontracker"])

# 辅助函数：判断当前时段
def get_current_period_info():
    """
    返回 (current_date, period_string)
    逻辑：14:00 之前算 morning，之后算 evening
    """
    now = timezone.localtime()
    today = now.date()
    # 14点为分界线
    if now.time() < time(14, 0):
        return today, EmotionRecord.PERIOD_MORNING
    else:
        return today, EmotionRecord.PERIOD_EVENING

@emotion_router.post("/", response=EmotionRecordResponseSchema, auth=jwt_auth)
def create_emotion_record(request, data: EmotionRecordCreateSchema):
    from apps.users.models import User
    current_user = request.auth
    
    # 1. 计算当前归属的日期和时段（由后端控制，不要信任前端传来的 period）
    record_date, period = get_current_period_info()

    # 2. 准备要更新/写入的数据 (defaults 字典)
    defaults_data = {
        "depression": data.depression,
        "anxiety": data.anxiety,
        "energy": data.energy,
        "sleep": data.sleep,
        "mainMood": getattr(data, "mainMood", None),
        "moodIntensity": getattr(data, "moodIntensity", None),
        "mainMoodOther": getattr(data, "mainMoodOther", None),
        "moodSupplementTags": getattr(data, "moodSupplementTags", None),
        "moodSupplementText": getattr(data, "moodSupplementText", None),
        "created_at": timezone.now() 
    }

    # 3. 核心逻辑：Update Or Create
    # 查找条件：user_id + record_date + period
    # 如果找到 -> 更新 defaults_data 中的字段
    # 如果没找到 -> 创建新记录
    record, created = EmotionRecord.objects.update_or_create(
        user_id=current_user.id,
        record_date=record_date,
        period=period,
        defaults=defaults_data
    )

    # 更新用户上次测试时间
    try:
        User.objects.filter(id=current_user.id).update(last_mood_tested_at=timezone.now())
    except Exception:
        pass

    return record  # Schema 会自动序列化 model 实例

@emotion_router.get("/status", auth=jwt_auth)
def get_today_status(request):
    current_user = request.auth
    if not current_user:
        return {"morning_filled": False, "evening_filled": False}
    
    now = timezone.localtime()
    today = now.date()
    
    # 现在的查询变得极其简单且极快，不需要计算时间范围
    records = EmotionRecord.objects.filter(
        user_id=current_user.id,
        record_date=today
    ).values_list('period', flat=True)
    
    # records 可能是 ['morning'] 或 ['morning', 'evening'] 或 []
    return {
        "morning_filled": EmotionRecord.PERIOD_MORNING in records,
        "evening_filled": EmotionRecord.PERIOD_EVENING in records
    }