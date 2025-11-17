"""用户反馈管理后台 - 原生基础版本"""
from django.contrib import admin
from apps.feedback.models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """用户反馈管理"""
    list_display = ['id', 'user', 'rating', 'content', 'created_at', 'is_processed']
    list_filter = ['rating', 'is_processed', 'created_at']
    search_fields = ['content', 'user__display_name', 'user__phone']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'rating', 'content')
        }),
        ('处理状态', {
            'fields': ('is_processed',)
        }),
        ('时间信息', {
            'fields': ('created_at',)
        }),
    )