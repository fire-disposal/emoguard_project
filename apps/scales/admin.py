"""
量表结果管理后台 - 重构版本，使用统一的基础组件
"""
from django.contrib import admin
from apps.common.admin_base import TimeBasedAdmin
from apps.common.resource_configs import ScaleResultResource
from apps.scales.models import ScaleResult


@admin.register(ScaleResult)
class ScaleResultAdmin(TimeBasedAdmin):
    """量表结果管理后台 - 简化版本"""
    
    resource_class = ScaleResultResource
    
    # 特有配置
    list_display = (
        "id",
        "user_info",
        "scale_code",
        "score",
        "started_at",
        "completed_at",
        "created_at",
    )
    search_fields = ("user_id", "scale_code")
    list_filter = ("scale_code", "started_at", "completed_at", "created_at")
    
    # 导出配置
    export_extra_fields = ["id", "scale_code", "score", "started_at", "completed_at", "created_at"]
    export_extra_titles = ["记录ID", "量表编码", "得分", "开始时间", "完成时间", "创建时间"]
