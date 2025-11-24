from ninja import Router, Query
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import MoodJournal
from .serializers import (
    MoodJournalCreateSchema, MoodJournalUpdateSchema, MoodJournalResponseSchema,
    MoodJournalListQuerySchema, MoodStatisticsSchema
)
from config.jwt_auth_adapter import jwt_auth

journals_router = Router(tags=["journals"])

@journals_router.get("/", response=list[MoodJournalResponseSchema], auth=jwt_auth)
def list_journals(request, filters: MoodJournalListQuerySchema = Query(...)):
    """
    获取情绪日记列表，支持多种过滤条件和分页
    """
    current_user = request.auth
    queryset = MoodJournal.objects.select_related('user')
    
    # 只显示当前用户的日记
    queryset = queryset.filter(user_id=current_user.id)
    
    # 日期范围过滤
    if filters.start_date:
        start_datetime = datetime.fromisoformat(filters.start_date)
        queryset = queryset.filter(record_date__gte=start_datetime)
    
    if filters.end_date:
        end_datetime = datetime.fromisoformat(filters.end_date)
        queryset = queryset.filter(record_date__lte=end_datetime)
    
    # 情绪名称过滤
    if filters.mainMood:
        queryset = queryset.filter(mainMood__icontains=filters.mainMood)
    
    # 分页
    start = (filters.page - 1) * filters.page_size
    end = start + filters.page_size
    journals = queryset[start:end]
    
    return [
        MoodJournalResponseSchema(
            id=j.id,
            mainMood=j.mainMood,
            moodIntensity=j.moodIntensity,
            mainMoodOther=j.mainMoodOther,
            moodSupplementTags=j.moodSupplementTags,
            moodSupplementText=j.moodSupplementText,
            record_date=j.record_date.isoformat(),
            created_at=j.created_at.isoformat()
        )
        for j in journals
    ]

@journals_router.get("/{journal_id}", response=MoodJournalResponseSchema)
def get_journal(request, journal_id: int):
    """
    获取单条情绪日记详情
    """
    journal = get_object_or_404(MoodJournal, id=journal_id)
    return MoodJournalResponseSchema(
        id=journal.id,
        mainMood=journal.mainMood,
        moodIntensity=journal.moodIntensity,
        mainMoodOther=journal.mainMoodOther,
        moodSupplementTags=journal.moodSupplementTags,
        moodSupplementText=journal.moodSupplementText,
        record_date=journal.record_date.isoformat(),
        created_at=journal.created_at.isoformat(),
    )

@journals_router.post("/", response=MoodJournalResponseSchema, auth=jwt_auth)
def create_journal(request, data: MoodJournalCreateSchema):
    """
    创建情绪日记
    """
    current_user = request.auth
    
    # 记录日期由模型自动生成，无需处理

    journal = MoodJournal.objects.create(
        user_id=current_user.id,
        mainMood=data.mainMood,
        moodIntensity=data.moodIntensity,
        mainMoodOther=data.mainMoodOther,
        moodSupplementTags=data.moodSupplementTags,
        moodSupplementText=data.moodSupplementText
    )
    
    return MoodJournalResponseSchema(
        id=journal.id,
        mainMood=journal.mainMood,
        moodIntensity=journal.moodIntensity,
        mainMoodOther=journal.mainMoodOther,
        moodSupplementTags=journal.moodSupplementTags,
        moodSupplementText=journal.moodSupplementText,
        record_date=journal.record_date.isoformat(),
        created_at=journal.created_at.isoformat(),
    )

@journals_router.put("/{journal_id}", response=MoodJournalResponseSchema, auth=jwt_auth)
def update_journal(request, journal_id: int, data: MoodJournalUpdateSchema):
    """
    更新情绪日记
    """
    current_user = request.auth
    journal = get_object_or_404(MoodJournal, id=journal_id)
    
    # 确保只能修改自己的日记
    if str(journal.user_id) != str(current_user.id):
        raise HttpError(403, "无权限修改他人的情绪日记")
    
    # 更新字段
    if data.mainMood is not None:
        journal.mainMood = data.mainMood
    if data.moodIntensity is not None:
        journal.moodIntensity = data.moodIntensity
    if data.mainMoodOther is not None:
        journal.mainMoodOther = data.mainMoodOther
    if data.moodSupplementTags is not None:
        journal.moodSupplementTags = data.moodSupplementTags
    if data.moodSupplementText is not None:
        journal.moodSupplementText = data.moodSupplementText
    
    journal.save()
    
    return MoodJournalResponseSchema(
        id=journal.id,
        mainMood=journal.mainMood,
        moodIntensity=journal.moodIntensity,
        mainMoodOther=journal.mainMoodOther,
        moodSupplementTags=journal.moodSupplementTags,
        moodSupplementText=journal.moodSupplementText,
        record_date=journal.record_date.isoformat(),
        created_at=journal.created_at.isoformat(),
    )

@journals_router.delete("/{journal_id}", auth=jwt_auth)
def delete_journal(request, journal_id: int):
    """
    删除情绪日记
    """
    current_user = request.auth
    journal = get_object_or_404(MoodJournal, id=journal_id)
    
    # 确保只能删除自己的日记
    if str(journal.user_id) != str(current_user.id):
        raise HttpError(403, "无权限删除他人的情绪日记")
    
    journal.delete()
    return {"success": True}

@journals_router.get("/statistics/daily", response=list[MoodStatisticsSchema], auth=jwt_auth)
def get_daily_statistics(request, days: int = Query(30)):
    """
    获取当前用户的日情绪统计
    """
    current_user = request.auth
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # 按日期分组统计
    statistics = MoodJournal.objects.filter(
        user_id=current_user.id,
        record_date__date__gte=start_date,
        record_date__date__lte=end_date
    ).values('record_date__date').annotate(
        avg_score=Avg('mood_score'),
        mood_count=Count('id'),
        dominant_mood=Count('mainMood')
    ).order_by('record_date__date')
    
    # 获取每个日期的主要情绪
    result = []
    for stat in statistics:
        # 获取该日期的主要情绪
        dominant_mood = MoodJournal.objects.filter(
            user_id=current_user.id,
            record_date__date=stat['record_date__date']
        ).values('mainMood').annotate(
            count=Count('id')
        ).order_by('-count').first()
        
        result.append(MoodStatisticsSchema(
            date=stat['record_date__date'].isoformat(),
            avg_score=round(stat['avg_score'], 2),
            mood_count=stat['mood_count'],
            dominant_mood=dominant_mood['mainMood'] if dominant_mood else '未知'
        ))
    
    return result

@journals_router.get("/trends/score", response=dict, auth=jwt_auth)
def get_mood_trends(request, days: int = Query(30)):
    """
    获取当前用户情绪分数趋势
    """
    current_user = request.auth
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    journals = MoodJournal.objects.filter(
        user_id=current_user.id,
        record_date__gte=start_date,
        record_date__lte=end_date
    ).order_by('record_date')
    
    dates = []
    scores = []
    
    for journal in journals:
        dates.append(journal.record_date.isoformat())
        scores.append(journal.mood_score)
    
    return {
        "dates": dates,
        "scores": scores,
        "average": sum(scores) / len(scores) if scores else 0,
        "trend": "上升" if len(scores) > 1 and scores[-1] > scores[0] else "下降" if len(scores) > 1 else "稳定"
    }
