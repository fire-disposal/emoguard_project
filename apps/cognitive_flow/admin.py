"""
认知测评流程管理后台
"""

from django.contrib import admin
from import_export.admin import ExportActionModelAdmin
from import_export import resources, fields
from apps.cognitive_flow.models import CognitiveAssessmentRecord
from apps.users.admin_mixins import BaseAdminMixin


class CognitiveAssessmentRecordResource(resources.ModelResource):
    """认知测评记录导出资源（仅保留核心业务字段，人口学信息由导出模块统一处理）"""

    id = fields.Field(column_name="记录ID", attribute="id")
    user_id_display = fields.Field(column_name="用户ID", attribute="user_id")
    score_scd = fields.Field(column_name="SCD得分", attribute="score_scd")
    score_mmse = fields.Field(column_name="MMSE得分", attribute="score_mmse")
    score_moca = fields.Field(column_name="MoCA得分", attribute="score_moca")
    score_gad7 = fields.Field(column_name="GAD7得分", attribute="score_gad7")
    score_phq9 = fields.Field(column_name="PHQ9得分", attribute="score_phq9")
    score_adl = fields.Field(column_name="ADL得分", attribute="score_adl")
    started_at = fields.Field(column_name="开始时间", attribute="started_at")
    completed_at = fields.Field(column_name="完成时间", attribute="completed_at")
    created_at = fields.Field(column_name="记录时间", attribute="created_at")

    class Meta:
        model = CognitiveAssessmentRecord
        fields = [
            "id",
            "user_id_display",
            "score_scd",
            "score_mmse",
            "score_moca",
            "score_gad7",
            "score_phq9",
            "score_adl",
            "started_at",
            "completed_at",
            "created_at",
        ]
        export_order = fields
        skip_unchanged = True


@admin.register(CognitiveAssessmentRecord)
class CognitiveAssessmentRecordAdmin(BaseAdminMixin, ExportActionModelAdmin):
    resource_class = CognitiveAssessmentRecordResource
    
    # 定义导出字段配置
    export_extra_fields = [
        "id", "score_scd", "score_mmse", "score_moca", "score_gad7", "score_phq9", "score_adl",
        "started_at", "completed_at", "created_at"
    ]
    export_extra_titles = [
        "记录ID", "SCD得分", "MMSE得分", "MoCA得分", "GAD7得分", "PHQ9得分", "ADL得分",
        "开始时间", "完成时间", "记录时间"
    ]
    
    list_display = (
        "id",
        "user_info",  # 使用统一的user_info方法
        "score_scd",
        "score_mmse",
        "score_moca",
        "score_gad7",
        "score_phq9",
        "score_adl",
        "started_at",
        "completed_at",
        "created_at",
    )
    list_display_links = ("id", "user_info")
    search_fields = ("user_id",)
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    actions = ["export_selected_excel", "export_selected_csv"]
    date_hierarchy = "created_at"
