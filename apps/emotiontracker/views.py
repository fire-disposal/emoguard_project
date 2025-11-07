from ninja import Router, Query
from django.utils import timezone
from datetime import datetime, time, timedelta
from .models import EmotionRecord
from .serializers import (
    EmotionRecordCreateSchema, EmotionRecordResponseSchema, EmotionTrendSchema
)

emotion_router = Router()

@emotion_router.post("/", response=EmotionRecordResponseSchema)
def create_emotion_record(request, data: EmotionRecordCreateSchema):
    record = EmotionRecord.objects.create(
        user_id=data.user_id,
        depression=data.depression,
        anxiety=data.anxiety,
        energy=data.energy,
        sleep=data.sleep
    )
    return EmotionRecordResponseSchema(
        id=record.id,
        user_id=str(record.user_id),
        depression=record.depression,
        anxiety=record.anxiety,
        energy=record.energy,
        sleep=record.sleep,
        created_at=record.created_at.isoformat()
    )

@emotion_router.get("/trend/{user_id}", response=EmotionTrendSchema)
def get_emotion_trend(request, user_id: str, days: int = Query(90)):
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    records = EmotionRecord.objects.filter(
        user_id=user_id,
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

@emotion_router.get("/status", auth=None)
def get_today_status(request):
    """
    返回今日早间/晚间是否已填写（自动识别当前用户）
    早晚分界线为14:00
    """
    user = getattr(request, "user", None)
    if not user or not getattr(user, "is_authenticated", False):
        return {"morning_filled": False, "evening_filled": False}
    now = timezone.localtime()
    today = now.date()
    morning_end = datetime.combine(today, time(14, 0, 0, tzinfo=now.tzinfo))
    morning_record = EmotionRecord.objects.filter(
        user_id=user.id,
        created_at__gte=datetime.combine(today, time(0, 0, 0, tzinfo=now.tzinfo)),
        created_at__lt=morning_end
    ).exists()
    evening_record = EmotionRecord.objects.filter(
        user_id=user.id,
        created_at__gte=morning_end,
        created_at__lt=datetime.combine(today + timedelta(days=1), time(0, 0, 0, tzinfo=now.tzinfo))
    ).exists()
    return {
        "morning_filled": morning_record,
        "evening_filled": evening_record
    }