"""报告模块的 admin 配置"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
import json
from apps.users.admin_mixins import UUIDUserAdminMixin, UserRealNameFilter
from .models import HealthReport


@admin.register(HealthReport)
class HealthReportAdmin(UUIDUserAdminMixin, admin.ModelAdmin):
    """健康报告管理"""
    
    list_display = [
        'id', 'user_real_name', 'report_type', 
        'overall_risk', 'created_at'
    ]
    
    list_filter = [
        'report_type', 'overall_risk', 'created_at', 
        UserRealNameFilter
    ]
    
    search_fields = [
        'report_type', 'summary', 'professional_advice'
    ]
    
    readonly_fields = [
        'id', 'user_id', 'created_at', 'updated_at',
        'recommendations_display', 'trend_data_display'
    ]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user_id', 'report_type', 'assessment_id')
        }),
        ('报告内容', {
            'fields': ('overall_risk', 'summary')
        }),
        ('专业建议', {
            'fields': ('professional_advice',),
            'classes': ('wide',)
        }),
        ('趋势分析', {
            'fields': ('trend_analysis', 'trend_data_display'),
            'classes': ('wide',)
        }),
        ('建议列表', {
            'fields': ('recommendations_display',),
            'classes': ('wide',)
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def recommendations_display(self, obj):
        """建议列表显示"""
        if obj.recommendations:
            try:
                if isinstance(obj.recommendations, list):
                    items = []
                    for i, rec in enumerate(obj.recommendations, 1):
                        if isinstance(rec, dict):
                            title = rec.get('title', f'建议 {i}')
                            content = rec.get('content', '')
                            items.append(f"<strong>{title}:</strong> {content}")
                        else:
                            items.append(f"{i}. {rec}")
                    return format_html("<br>".join(items))
                else:
                    return str(obj.recommendations)
            except Exception:
                return "格式错误"
        return "无建议"
    
    recommendations_display.short_description = '建议列表'
    recommendations_display.allow_tags = True
    
    def trend_data_display(self, obj):
        """趋势数据显示"""
        if obj.trend_data:
            try:
                # 格式化 JSON 数据
                formatted = json.dumps(obj.trend_data, ensure_ascii=False, indent=2)
                return format_html(
                    '<pre style="background: #f8f9fa; padding: 10px; '
                    'border: 1px solid #dee2e6; border-radius: 4px; '
                    'max-height: 300px; overflow-y: auto;">{}</pre>',
                    formatted
                )
            except Exception:
                return "数据格式错误"
        return "无趋势数据"
    
    trend_data_display.short_description = '趋势数据'
    trend_data_display.allow_tags = True
    
    def risk_level_display(self, obj):
        """风险等级显示"""
        risk_colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#dc3545',
            'critical': '#721c24'
        }
        
        color = risk_colors.get(obj.overall_risk.lower(), '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_overall_risk_display()
        )
    
    risk_level_display.short_description = '风险等级'
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request)
    
    def has_add_permission(self, request):
        """禁止手动添加健康报告"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """只允许查看，不允许修改"""
        return False