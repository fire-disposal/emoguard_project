"""认知流模块的 admin 配置"""
from django.contrib import admin
from django.utils.html import format_html
from apps.users.admin_mixins import UUIDUserAdminMixin, UserRealNameFilter
from .models import CognitiveAssessmentRecord


@admin.register(CognitiveAssessmentRecord)
class CognitiveAssessmentRecordAdmin(UUIDUserAdminMixin, admin.ModelAdmin):
    """认知测评答卷管理"""
    
    list_display = [
        'id', 'user_real_name', 'score_summary', 
        'started_at', 'completed_at', 'duration_display',
        'created_at'
    ]
    
    list_filter = [
        'created_at', 'started_at', 'completed_at',
        UserRealNameFilter
    ]
    
    search_fields = [
        'analysis'
    ]
    
    readonly_fields = [
        'id', 'user_id', 'created_at', 'updated_at',
        'duration_display'
    ]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user_id', 'started_at', 'completed_at', 'duration_display')
        }),
        ('测评得分', {
            'fields': (
                'score_scd', 'score_mmse', 'score_moca',
                'score_gad7', 'score_phq9', 'score_adl'
            )
        }),
        ('分析结果', {
            'fields': ('analysis',),
            'classes': ('wide',)
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def score_summary(self, obj):
        """得分摘要"""
        scores = []
        score_fields = [
            ('score_scd', 'SCD'),
            ('score_mmse', 'MMSE'),
            ('score_moca', 'MoCA'),
            ('score_gad7', 'GAD-7'),
            ('score_phq9', 'PHQ-9'),
            ('score_adl', 'ADL')
        ]
        
        for field_name, label in score_fields:
            value = getattr(obj, field_name)
            if value is not None:
                scores.append(f"{label}: {value}")
        
        return " | ".join(scores) if scores else "无得分记录"
    
    score_summary.short_description = '得分摘要'
    
    def duration_display(self, obj):
        """显示测评时长"""
        if obj.started_at and obj.completed_at:
            duration = obj.completed_at - obj.started_at
            minutes = duration.total_seconds() / 60
            return f"{minutes:.1f} 分钟"
        return "-"
    
    duration_display.short_description = '测评时长'
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request)
    
    def has_add_permission(self, request):
        """禁止手动添加认知测评记录"""
        return False