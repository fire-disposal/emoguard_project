"""
认知测评流程管理后台
"""

from django.contrib import admin
from apps.scales.admin.demographic_export import (
    build_excel_with_demographics,
    build_csv_with_demographics,
)
from import_export.admin import ExportActionModelAdmin
from import_export import resources, fields
from apps.cognitive_flow.models import CognitiveAssessmentRecord

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
class CognitiveAssessmentRecordAdmin(ExportActionModelAdmin):
    resource_class = CognitiveAssessmentRecordResource
    list_display = (
        "id",
        "user_info",
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

    def export_selected_excel(self, request, queryset):
        """导出认知测评记录为Excel格式（调用人口学信息导出工具）"""
        extra_field_order = [
            "id", "score_scd", "score_mmse", "score_moca", "score_gad7", "score_phq9", "score_adl",
            "started_at", "completed_at", "created_at"
        ]
        extra_field_titles = [
            "记录ID", "SCD得分", "MMSE得分", "MoCA得分", "GAD7得分", "PHQ9得分", "ADL得分",
            "开始时间", "完成时间", "记录时间"
        ]
        def get_user_id(record):
            return record.user_id
        return build_excel_with_demographics(queryset, get_user_id, extra_field_order, extra_field_titles)

    export_selected_excel.short_description = "导出为Excel"

    def export_selected_csv(self, request, queryset):
        """导出认知测评记录为CSV格式（调用人口学信息导出工具）"""
        extra_field_order = [
            "id", "score_scd", "score_mmse", "score_moca", "score_gad7", "score_phq9", "score_adl",
            "started_at", "completed_at", "created_at"
        ]
        extra_field_titles = [
            "记录ID", "SCD得分", "MMSE得分", "MoCA得分", "GAD7得分", "PHQ9得分", "ADL得分",
            "开始时间", "完成时间", "记录时间"
        ]
        def get_user_id(record):
            return record.user_id
        return build_csv_with_demographics(queryset, get_user_id, extra_field_order, extra_field_titles)

    export_selected_csv.short_description = "导出为CSV"

    def user_info(self, obj):
        """显示用户信息（仅显示ID）"""
        return f"ID: {str(obj.user_id)[:8]}"
    user_info.short_description = "用户信息"
