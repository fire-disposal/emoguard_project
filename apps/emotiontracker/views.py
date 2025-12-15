from ninja import Router
from django.utils import timezone
from datetime import time, timedelta
from .models import EmotionRecord
from .serializers import (
    EmotionRecordCreateSchema, EmotionRecordResponseSchema, EmotionTrendSchema
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

    # 保证 started_at 字段序列化为字符串（空字符串而非 None）
    result = {
        "id": record.id,
        "depression": record.depression,
        "anxiety": record.anxiety,
        "energy": record.energy,
        "sleep": record.sleep,
        "mainMood": record.mainMood,
        "moodIntensity": record.moodIntensity,
        "mainMoodOther": record.mainMoodOther,
        "moodSupplementTags": record.moodSupplementTags,
        "moodSupplementText": record.moodSupplementText,
        "period": record.period,
        "started_at": record.started_at.isoformat() if record.started_at else "",
    }
    return result

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

# 如需新增批量/列表API，务必保证 started_at 字段序列化为字符串（空字符串而非 None）
@emotion_router.get("/list", response=list[EmotionRecordResponseSchema], auth=jwt_auth)
def list_emotion_records(request):
    current_user = request.auth
    queryset = EmotionRecord.objects.filter(user_id=current_user.id).order_by("-created_at")
    result = []
    for record in queryset:
        result.append({
            "id": record.id,
            "depression": record.depression,
            "anxiety": record.anxiety,
            "energy": record.energy,
            "sleep": record.sleep,
            "mainMood": record.mainMood,
            "moodIntensity": record.moodIntensity,
            "mainMoodOther": record.mainMoodOther,
            "moodSupplementTags": record.moodSupplementTags,
            "moodSupplementText": record.moodSupplementText,
            "period": record.period,
            "started_at": record.started_at.isoformat() if record.started_at else "",
        })
    return result

@emotion_router.get("/trend", response=EmotionTrendSchema, auth=jwt_auth)
def get_emotion_trend(request, days: int = 30):
    """
    获取用户情绪趋势数据
    返回指定天数内的每日情绪数据，每天可能有morning/evening两个时段
    如果某天有多个时段，取平均值
    """
    current_user = request.auth
    if not current_user:
        return {"dates": [], "depression": [], "anxiety": [], "energy": [], "sleep": []}
    
    # 计算日期范围
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days - 1)
    
    # 查询指定范围内的所有记录
    records = EmotionRecord.objects.filter(
        user_id=current_user.id,
        record_date__range=[start_date, end_date]
    ).order_by('record_date', 'period')
    
    # 按日期分组，计算每日平均值
    daily_data = {}
    for record in records:
        date_str = record.record_date.strftime('%Y-%m-%d')
        if date_str not in daily_data:
            daily_data[date_str] = {
                'depression': [],
                'anxiety': [],
                'energy': [],
                'sleep': []
            }
        
        daily_data[date_str]['depression'].append(record.depression)
        daily_data[date_str]['anxiety'].append(record.anxiety)
        daily_data[date_str]['energy'].append(record.energy)
        daily_data[date_str]['sleep'].append(record.sleep)
    
    # 构建趋势数据
    dates = []
    depression = []
    anxiety = []
    energy = []
    sleep = []
    
    # 按日期顺序处理
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        dates.append(date_str)
        
        if date_str in daily_data:
            # 计算平均值（四舍五入到整数）
            depression.append(round(sum(daily_data[date_str]['depression']) / len(daily_data[date_str]['depression'])))
            anxiety.append(round(sum(daily_data[date_str]['anxiety']) / len(daily_data[date_str]['anxiety'])))
            energy.append(round(sum(daily_data[date_str]['energy']) / len(daily_data[date_str]['energy'])))
            sleep.append(round(sum(daily_data[date_str]['sleep']) / len(daily_data[date_str]['sleep'])))
        else:
            # 没有数据的日期用0填充
            depression.append(0)
            anxiety.append(0)
            energy.append(0)
            sleep.append(0)
        
        current_date += timedelta(days=1)
    
    return {
        "dates": dates,
        "depression": depression,
        "anxiety": anxiety,
        "energy": energy,
        "sleep": sleep
    }