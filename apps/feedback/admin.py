"""用户反馈管理后台 - 重构版本，使用统一的基础组件"""
from django.contrib import admin
from apps.common.admin_base import BaseModelAdmin
from apps.common.resource_configs import FeedbackResource
from apps.feedback.models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(BaseModelAdmin):
    """用户反馈管理后台 - 简化版本"""
    
    resource_class = FeedbackResource
    
    # 特有配置
    list_display = ['id', 'user_info', 'rating', 'content', 'is_processed', 'created_at']
    search_fields = ['content', 'user__display_name', 'user__phone']
    list_filter = ['rating', 'is_processed', 'created_at']
    
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
    
    # 导出配置
    export_extra_fields = ["id", "rating", "content", "is_processed", "created_at"]
    export_extra_titles = ["反馈ID", "评分", "反馈内容", "已处理", "创建时间"]