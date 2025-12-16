"""
健康报告管理后台 - 重构版本，使用统一的基础组件
"""
from django.contrib import admin
from apps.common.admin_base import BaseModelAdmin
from apps.common.resource_configs import HealthReportResource
from apps.reports.models import HealthReport


@admin.register(HealthReport)
class HealthReportAdmin(BaseModelAdmin):
    """健康报告管理后台 - 简化版本"""
    
    resource_class = HealthReportResource
    
    # 特有配置
    list_display = ('id', 'user_info', 'assessment_id', 'report_type', 'overall_risk', 'created_at')
    search_fields = ('user_id', 'assessment_id', 'report_type', 'overall_risk')
    list_filter = ('report_type', 'overall_risk', 'created_at')
    
    # 导出配置
    export_extra_fields = ["id", "assessment_id", "report_type", "overall_risk", "created_at"]
    export_extra_titles = ["报告ID", "测评记录ID", "报告类型", "整体风险", "创建时间"]