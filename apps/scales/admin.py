"""量表模块的 admin 配置"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
import json
from apps.users.admin_mixins import UUIDUserAdminMixin, UserRealNameFilter
from .models import ScaleResult


@admin.register(ScaleResult)
class ScaleResultAdmin(UUIDUserAdminMixin, admin.ModelAdmin):
    """量表结果管理"""
    
    list_display = [
        'id', 'user_real_name', 'scale_code', 
        'score', 'duration_display', 'created_at'
    ]
    
    list_filter = [
        'scale_code', 'created_at', UserRealNameFilter
    ]
    
    search_fields = [
        'scale_code', 'conclusion'
    ]
    
    readonly_fields = [
        'id', 'user_id', 'created_at', 'duration_display',
        'selected_options_display'
    ]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user_id', 'scale_code', 'score')
        }),
        ('答题详情', {
            'fields': ('selected_options_display',),
            'classes': ('wide',)
        }),
        ('结论', {
            'fields': ('conclusion',),
            'classes': ('wide',)
        }),
        ('时间信息', {
            'fields': ('started_at', 'completed_at', 'duration_display', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def selected_options_display(self, obj):
        """选项选择显示"""
        if obj.selected_options:
            try:
                if isinstance(obj.selected_options, list):
                    items = []
                    for i, option in enumerate(obj.selected_options, 1):
                        if isinstance(option, dict):
                            question = option.get('question', f'问题 {i}')
                            answer = option.get('answer', '')
                            items.append(f"<strong>{question}:</strong> {answer}")
                        else:
                            items.append(f"{i}. {option}")
                    return format_html("<br>".join(items))
                else:
                    # 如果是其他格式，尝试格式化为 JSON
                    formatted = json.dumps(obj.selected_options, ensure_ascii=False, indent=2)
                    return format_html(
                        '<pre style="background: #f8f9fa; padding: 10px; '
                        'border: 1px solid #dee2e6; border-radius: 4px;">{}</pre>',
                        formatted
                    )
            except Exception:
                return "数据格式错误"
        return "无选项数据"
    
    selected_options_display.short_description = '选项选择'
    selected_options_display.allow_tags = True
    
    def duration_display(self, obj):
        """显示答题时长"""
        if obj.started_at and obj.completed_at:
            duration = obj.completed_at - obj.started_at
            minutes = duration.total_seconds() / 60
            return f"{minutes:.1f} 分钟"
        return "-"
    
    duration_display.short_description = '答题时长'
    
    def score_level(self, obj):
        """分数等级显示"""
        # 根据量表类型和分数显示等级
        if obj.scale_code == 'gad7':
            if obj.score <= 4:
                return format_html('<span style="color: #28a745;">正常</span>')
            elif obj.score <= 9:
                return format_html('<span style="color: #ffc107;">轻度焦虑</span>')
            elif obj.score <= 14:
                return format_html('<span style="color: #fd7e14;">中度焦虑</span>')
            else:
                return format_html('<span style="color: #dc3545;">重度焦虑</span>')
        elif obj.scale_code == 'phq9':
            if obj.score <= 4:
                return format_html('<span style="color: #28a745;">正常</span>')
            elif obj.score <= 9:
                return format_html('<span style="color: #ffc107;">轻度抑郁</span>')
            elif obj.score <= 14:
                return format_html('<span style="color: #fd7e14;">中度抑郁</span>')
            elif obj.score <= 19:
                return format_html('<span style="color: #dc3545;">中重度抑郁</span>')
            else:
                return format_html('<span style="color: #721c24;">重度抑郁</span>')
        
        return "未知"
    
    score_level.short_description = '等级'
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request)
    
    def has_add_permission(self, request):
        """禁止手动添加量表结果"""
        return False
    
    actions = ['export_selected']
    
    def export_selected(self, request, queryset):
        """导出选中的量表结果"""
        # 这里可以添加导出功能
        self.message_user(request, f'已选择 {queryset.count()} 条记录进行导出')
    
    export_selected.short_description = '导出选中的记录'