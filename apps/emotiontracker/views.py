from ninja import Router, Query
from django.utils import timezone
from datetime import datetime, time, timedelta
from .models import EmotionRecord
from .serializers import (
    EmotionRecordCreateSchema, EmotionRecordResponseSchema, EmotionTrendSchema
)
from config.jwt_auth_adapter import jwt_auth

emotion_router = Router(tags=["emotiontracker"])

@emotion_router.post("/", response=EmotionRecordResponseSchema, auth=jwt_auth)
def create_emotion_record(request, data: EmotionRecordCreateSchema):
    from apps.users.models import User
    from django.utils import timezone

    current_user = request.auth
    record = EmotionRecord.objects.create(
        user_id=current_user.id,
        depression=data.depression,
        anxiety=data.anxiety,
        energy=data.energy,
        sleep=data.sleep,
        mainMood=getattr(data, "mainMood", None),
        moodIntensity=getattr(data, "moodIntensity", None),
        mainMoodOther=getattr(data, "mainMoodOther", None),
        moodSupplementTags=getattr(data, "moodSupplementTags", None),
        moodSupplementText=getattr(data, "moodSupplementText", None),
        period=getattr(data, "period", None),
        device_info=getattr(data, "device_info", None)
    )
    # 更新用户上次情绪测试时间
    try:
        User.objects.filter(id=current_user.id).update(last_mood_tested_at=timezone.now())
    except Exception:
        pass

    return EmotionRecordResponseSchema(
        id=record.id,
        user_id=str(record.user_id),
        depression=record.depression,
        anxiety=record.anxiety,
        energy=record.energy,
        sleep=record.sleep,
        mainMood=record.mainMood,
        moodIntensity=record.moodIntensity,
        mainMoodOther=record.mainMoodOther,
        moodSupplementTags=record.moodSupplementTags,
        moodSupplementText=record.moodSupplementText,
        period=record.period,
        device_info=record.device_info,
        created_at=record.created_at.isoformat()
    )

@emotion_router.get("/trend", response=EmotionTrendSchema, auth=jwt_auth)
def get_emotion_trend(request, days: int = Query(90)):
    current_user = request.auth
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    records = EmotionRecord.objects.filter(
        user_id=current_user.id,
        created_at__gte=start_date,
        created_at__lte=end_date
    ).order_by('created_at')

    dates = []
    depression = []
    anxiety = []
    energy = []
    sleep = []

    for r in records:
        dates.append(r.created_at.date().isoformat())
        depression.append(r.depression)
        anxiety.append(r.anxiety)
        energy.append(r.energy)
        sleep.append(r.sleep)

    return EmotionTrendSchema(
        dates=dates,
        depression=depression,
        anxiety=anxiety,
        energy=energy,
        sleep=sleep
    )

@emotion_router.get("/status", auth=jwt_auth)
def get_today_status(request):
    """
    返回今日早间/晚间是否已填写（自动识别当前用户）
    早晚分界线为14:00
    """
    # 使用JWT认证获取当前用户
    current_user = request.auth
    if not current_user:
        return {"morning_filled": False, "evening_filled": False}
    
    now = timezone.localtime()
    today = now.date()
    morning_end = datetime.combine(today, time(14, 0, 0, tzinfo=now.tzinfo))
    
    # 查询早间记录 (00:00-14:00)
    morning_record = EmotionRecord.objects.filter(
        user_id=current_user.id,
        created_at__gte=datetime.combine(today, time(0, 0, 0, tzinfo=now.tzinfo)),
        created_at__lt=morning_end
    ).exists()
    
    # 查询晚间记录 (14:00-次日00:00)
    evening_record = EmotionRecord.objects.filter(
        user_id=current_user.id,
        created_at__gte=morning_end,
        created_at__lt=datetime.combine(today + timedelta(days=1), time(0, 0, 0, tzinfo=now.tzinfo))
    ).exists()
    
    return {
        "morning_filled": morning_record,
        "evening_filled": evening_record
    }