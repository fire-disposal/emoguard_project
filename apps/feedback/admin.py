"""用户反馈模块的 admin 配置"""
from django.contrib import admin
from django.utils.html import format_html
from apps.users.admin_mixins import ForeignKeyUserAdminMixin, UserRealNameFilter
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(ForeignKeyUserAdminMixin, admin.ModelAdmin):
    """用户反馈管理"""
    
    list_display = [
        'id', 'user_real_name', 'rating_display', 
        'content_summary', 'is_processed', 'created_at'
    ]
    
    list_filter = [
        'rating', 'is_processed', 'created_at', 
        UserRealNameFilter
    ]
    
    search_fields = [
        'content'
    ]
    
    readonly_fields = [
        'id', 'created_at'
    ]
    
    fieldsets = (
        ('反馈信息', {
            'fields': ('user', 'rating', 'content')
        }),
        ('处理状态', {
            'fields': ('is_processed',)
        }),
        ('时间信息', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def rating_display(self, obj):
        """星级显示"""
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html(
            '<span style="color: #ffa500;">{}</span> ({}/5)',
            stars, obj.rating
        )
    
    rating_display.short_description = '评分'
    rating_display.admin_order_field = 'rating'
    
    def content_summary(self, obj):
        """内容摘要"""
        if obj.content:
            return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
        return "无内容"
    
    content_summary.short_description = '反馈内容'
    
    def get_queryset(self, request):
        """优化查询，预取用户信息"""
        return super().get_queryset(request).select_related('user')
    
    actions = ['mark_as_processed', 'mark_as_unprocessed']
    
    def mark_as_processed(self, request, queryset):
        """标记为已处理"""
        updated = queryset.update(is_processed=True)
        self.message_user(request, f'已将 {updated} 条反馈标记为已处理')
    
    mark_as_processed.short_description = '标记为已处理'
    
    def mark_as_unprocessed(self, request, queryset):
        """标记为未处理"""
        updated = queryset.update(is_processed=False)
        self.message_user(request, f'已将 {updated} 条反馈标记为未处理')
    
    mark_as_unprocessed.short_description = '标记为未处理'