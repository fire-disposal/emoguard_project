"""情绪日记模块的 admin 配置"""
from django.contrib import admin
from django.utils.html import format_html
from apps.users.admin_mixins import ForeignKeyUserAdminMixin, UserRealNameFilter
from .models import MoodJournal


@admin.register(MoodJournal)
class MoodJournalAdmin(ForeignKeyUserAdminMixin, admin.ModelAdmin):
    """情绪日记管理"""
    
    list_display = [
        'id', 'user_real_name', 'mood_summary', 
        'moodIntensity', 'record_date', 'created_at'
    ]
    
    list_filter = [
        'record_date', 'created_at', 
        UserRealNameFilter, 'mainMood'
    ]
    
    search_fields = [
        'mainMood', 'mainMoodOther', 'moodSupplementText'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'started_at'
    ]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user',)
        }),
        ('情绪信息', {
            'fields': ('mainMood', 'moodIntensity', 'mainMoodOther')
        }),
        ('补充信息', {
            'fields': ('moodSupplementTags', 'moodSupplementText')
        }),
        ('时间信息', {
            'fields': ('started_at',),
            'classes': ('collapse',)
        })
    )
    
    def mood_summary(self, obj):
        """情绪摘要"""
        mood_info = []
        if obj.mainMood:
            mood_info.append(f"情绪: {obj.mainMood}")
        if obj.moodIntensity:
            mood_info.append(f"强度: {obj.moodIntensity}")
        if obj.mainMoodOther:
            mood_info.append(f"其他: {obj.mainMoodOther}")
        
        return " | ".join(mood_info) if mood_info else "无情绪描述"
    
    mood_summary.short_description = '情绪摘要'
    
    def get_queryset(self, request):
        """优化查询，预取用户信息"""
        return super().get_queryset(request).select_related('user')
    
    def has_add_permission(self, request):
        """禁止手动添加情绪日记"""
        return False