"""通知管理后台 - NinjaAPI风格"""
from django.contrib import admin
from apps.notice.models import UserQuota, NotificationLog


@admin.register(UserQuota)
class UserQuotaAdmin(admin.ModelAdmin):
    """用户订阅额度管理"""
    list_display = ['id', 'user', 'template_id', 'count', 'updated_at']
    list_filter = ['template_id', 'updated_at']
    search_fields = ['user__username', 'template_id']
    readonly_fields = ['updated_at']
    ordering = ['-updated_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'template_id', 'count')
        }),
        ('时间信息', {
            'fields': ('updated_at',)
        }),
    )

    def has_add_permission(self, request):
        # 通常不建议手动添加，通过API自动管理
        return False


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    """通知发送日志管理"""
    list_display = ['id', 'user', 'template_id', 'status', 'created_at', 'sent_at']
    list_filter = ['status', 'template_id', 'created_at']
    search_fields = ['user__username', 'template_id', 'error_response']
    readonly_fields = ['created_at', 'sent_at', 'wechat_msg_id']
    ordering = ['-created_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'template_id', 'message_data', 'assessment_id')
        }),
        ('状态信息', {
            'fields': ('status', 'wechat_msg_id', 'error_response')
        }),
        ('时间信息', {
            'fields': ('created_at', 'sent_at')
        }),
    )

    def has_add_permission(self, request):
        # 不允许手动添加，通过系统自动记录
        return False

    def has_change_permission(self, request, obj=None):
        # 只允许查看，不允许修改
        return False