from django.contrib import admin
from import_export.admin import ExportActionModelAdmin
from apps.scales.models import ScaleResult
from apps.users.admin_mixins import BaseAdminMixin


@admin.register(ScaleResult)
class ScaleResultAdmin(BaseAdminMixin, ExportActionModelAdmin):
    # 定义导出字段配置
    export_extra_fields = [
        "id", "scale_code", "score", "started_at", "completed_at", "created_at"
    ]
    export_extra_titles = [
        "记录ID", "量表编码", "得分", "开始时间", "完成时间", "创建时间"
    ]
    
    list_display = (
        "id",
        "user_info",  # 使用统一的user_info方法
        "scale_code",
        "score",
        "started_at",
        "completed_at",
        "created_at",
    )
    search_fields = ("user_id", "scale_code")
    list_filter = ("scale_code", "started_at", "completed_at", "created_at")
    actions = ["export_selected_excel", "export_selected_csv"]
