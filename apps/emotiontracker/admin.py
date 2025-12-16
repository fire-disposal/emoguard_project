"""情绪追踪模块的 admin 配置"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from apps.users.admin_mixins import UUIDUserAdminMixin, UserRealNameFilter
from .models import EmotionRecord


@admin.register(EmotionRecord)
class EmotionRecordAdmin(UUIDUserAdminMixin, admin.ModelAdmin):
    """情绪记录管理"""
    
    list_display = [
        'id', 'user_real_name', 'record_date', 'period', 
        'depression', 'anxiety', 'energy', 'sleep', 
        'mainMood', 'moodIntensity', 'created_at'
    ]
    
    list_filter = [
        'period', 'record_date', 'created_at', 
        UserRealNameFilter, 'mainMood'
    ]
    
    search_fields = [
        'mainMood', 'mainMoodOther', 'moodSupplementText'
    ]
    
    readonly_fields = [
        'id', 'user_id', 'created_at', 'started_at'
    ]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user_id', 'record_date', 'period')
        }),
        ('情绪评分', {
            'fields': ('depression', 'anxiety', 'energy', 'sleep')
        }),
        ('情绪描述', {
            'fields': ('mainMood', 'moodIntensity', 'mainMoodOther')
        }),
        ('补充信息', {
            'fields': ('moodSupplementTags', 'moodSupplementText')
        }),
        ('时间信息', {
            'fields': ('started_at', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related()
    
    def mood_summary(self, obj):
        """情绪摘要"""
        mood_info = []
        if obj.mainMood:
            mood_info.append(f"主要情绪: {obj.mainMood}")
        if obj.moodIntensity:
            mood_info.append(f"强度: {obj.moodIntensity}")
        if obj.moodSupplementText:
            mood_info.append(f"补充: {obj.moodSupplementText[:50]}...")
        
        return " | ".join(mood_info) if mood_info else "无描述"
    
    mood_summary.short_description = '情绪摘要'
    
    def score_summary(self, obj):
        """评分摘要"""
        scores = []
        if obj.depression is not None:
            scores.append(f"抑郁: {obj.depression}")
        if obj.anxiety is not None:
            scores.append(f"焦虑: {obj.anxiety}")
        if obj.energy is not None:
            scores.append(f"精力: {obj.energy}")
        if obj.sleep is not None:
            scores.append(f"睡眠: {obj.sleep}")
        
        return " | ".join(scores) if scores else "无评分"
    
    score_summary.short_description = '评分摘要'
    
    def has_add_permission(self, request):
        """禁止手动添加情绪记录"""
        return False