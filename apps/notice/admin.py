"""通知模块的 admin 配置"""
from django.contrib import admin
from django.utils.html import format_html
from apps.users.admin_mixins import ForeignKeyUserAdminMixin, UserRealNameFilter
from .models import UserQuota, NotificationLog


@admin.register(UserQuota)
class UserQuotaAdmin(ForeignKeyUserAdminMixin, admin.ModelAdmin):
    """用户订阅额度管理"""
    
    list_display = [
        'id', 'user_real_name', 'template_id', 
        'count', 'updated_at'
    ]
    
    list_filter = [
        'template_id', 'updated_at', UserRealNameFilter
    ]
    
    search_fields = [
        'template_id'
    ]
    
    readonly_fields = [
        'id', 'updated_at'
    ]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'template_id', 'count')
        }),
        ('时间信息', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """优化查询，预取用户信息"""
        return super().get_queryset(request).select_related('user')
    
    actions = ['reset_quota', 'increase_quota', 'decrease_quota']
    
    def reset_quota(self, request, queryset):
        """重置额度为0"""
        updated = queryset.update(count=0)
        self.message_user(request, f'已重置 {updated} 个用户的订阅额度')
    
    reset_quota.short_description = '重置额度为0'
    
    def increase_quota(self, request, queryset):
        """增加额度"""
        for quota in queryset:
            quota.count += 1
            quota.save()
        self.message_user(request, f'已为 {queryset.count()} 个用户增加1次订阅额度')
    
    increase_quota.short_description = '增加1次额度'
    
    def decrease_quota(self, request, queryset):
        """减少额度"""
        for quota in queryset:
            if quota.count > 0:
                quota.count -= 1
                quota.save()
        self.message_user(request, f'已为 {queryset.count()} 个用户减少1次订阅额度')
    
    decrease_quota.short_description = '减少1次额度'


@admin.register(NotificationLog)
class NotificationLogAdmin(ForeignKeyUserAdminMixin, admin.ModelAdmin):
    """通知发送日志管理"""
    
    list_display = [
        'id', 'user_real_name', 'template_id_short', 
        'status_display', 'created_at', 'sent_at'
    ]
    
    list_filter = [
        'status', 'template_id', 'created_at', 
        UserRealNameFilter
    ]
    
    search_fields = [
        'template_id', 'message_data', 'error_response'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'sent_at', 'wechat_msg_id',
        'error_response'
    ]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'template_id', 'status')
        }),
        ('消息内容', {
            'fields': ('message_data',),
            'classes': ('wide',)
        }),
        ('业务关联', {
            'fields': ('assessment_id',),
            'classes': ('collapse',)
        }),
        ('发送信息', {
            'fields': ('wechat_msg_id', 'error_response'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'sent_at'),
            'classes': ('collapse',)
        })
    )
    
    def template_id_short(self, obj):
        """模板ID简写"""
        if len(obj.template_id) > 20:
            return obj.template_id[:20] + '...'
        return obj.template_id
    
    template_id_short.short_description = '模板ID'
    template_id_short.admin_order_field = 'template_id'
    
    def status_display(self, obj):
        """状态显示"""
        status_colors = {
            'pending': '#ffc107',
            'success': '#28a745',
            'failed': '#dc3545'
        }
        status_labels = {
            'pending': '等待发送',
            'success': '发送成功',
            'failed': '发送失败'
        }
        
        color = status_colors.get(obj.status, '#6c757d')
        label = status_labels.get(obj.status, obj.status)
        
        return format_html(
            '<span style="color: {};">● {}</span>',
            color, label
        )
    
    status_display.short_description = '状态'
    status_display.admin_order_field = 'status'
    
    def get_queryset(self, request):
        """优化查询，预取用户信息"""
        return super().get_queryset(request).select_related('user')
    
    def has_add_permission(self, request):
        """禁止手动添加通知日志"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """只允许查看，不允许修改"""
        return False
