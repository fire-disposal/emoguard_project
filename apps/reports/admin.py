from django.contrib import admin
from import_export.admin import ExportActionModelAdmin
from apps.reports.models import HealthReport
from apps.users.admin_mixins import BaseAdminMixin


@admin.register(HealthReport)
class HealthReportAdmin(BaseAdminMixin, ExportActionModelAdmin):
    # 定义导出字段配置
    export_extra_fields = [
        "id", "assessment_id", "report_type", "overall_risk", "created_at"
    ]
    export_extra_titles = [
        "报告ID", "测评记录ID", "报告类型", "整体风险", "创建时间"
    ]
    
    list_display = ('id', 'user_info', 'assessment_id', 'report_type', 'overall_risk', 'created_at')  # 使用统一的user_info
    search_fields = ('user_id', 'assessment_id', 'report_type', 'overall_risk')
    list_filter = ('report_type', 'overall_risk', 'created_at')
    actions = ["export_selected_excel", "export_selected_csv"]