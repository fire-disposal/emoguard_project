"""
情绪记录管理后台
"""

from django.contrib import admin
from import_export.admin import ExportActionModelAdmin
from import_export import resources, fields
from apps.emotiontracker.models import EmotionRecord


class EmotionRecordResource(resources.ModelResource):
    """情绪记录导出资源（ID转字符串，人口学信息由导出模块统一处理）"""

    id = fields.Field(column_name="记录ID", attribute="id")
    user_id_display = fields.Field(column_name="用户ID", attribute="user_id")
    period = fields.Field(column_name="时段", attribute="period")
    depression = fields.Field(column_name="抑郁得分", attribute="depression")
    anxiety = fields.Field(column_name="焦虑得分", attribute="anxiety")
    energy = fields.Field(column_name="精力得分", attribute="energy")
    sleep = fields.Field(column_name="睡眠得分", attribute="sleep")
    mainMood = fields.Field(column_name="主要情绪", attribute="mainMood")
    moodIntensity = fields.Field(column_name="情绪强度", attribute="moodIntensity")
    moodSupplementTags = fields.Field(
        column_name="情绪标签", attribute="moodSupplementTags"
    )
    moodSupplementText = fields.Field(
        column_name="补充说明", attribute="moodSupplementText"
    )
    created_at = fields.Field(column_name="记录时间", attribute="created_at")

    def dehydrate_id(self, obj):
        return str(obj.id)

    class Meta:
        model = EmotionRecord
        fields = [
            "id",
            "user_id_display",
            "period",
            "depression",
            "anxiety",
            "energy",
            "sleep",
            "mainMood",
            "moodIntensity",
            "moodSupplementTags",
            "moodSupplementText",
            "created_at",
        ]
        export_order = fields
        skip_unchanged = True


@admin.register(EmotionRecord)
class EmotionRecordAdmin(ExportActionModelAdmin):
    resource_class = EmotionRecordResource
    list_display = (
        "id",
        "user_id",
        "period",
        "depression",
        "anxiety",
        "energy",
        "sleep",
        "mainMood",
        "moodIntensity",
        "moodSupplementTags",
        "moodSupplementText",
        "created_at",
    )
    search_fields = ("user_id", "mainMood", "period")
    list_filter = ("period", "mainMood", "moodIntensity", "created_at")
    readonly_fields = ("created_at",)
    list_per_page = 25
    ordering = ("-created_at",)
    actions = ["export_selected_excel", "export_selected_csv"]
    date_hierarchy = "created_at"

    def export_selected_excel(self, request, queryset):
        """导出心情日志为Excel格式（调用人口学信息导出工具）"""
        from apps.users.demographic_export import build_excel_with_demographics

        extra_field_order = [
            "id",
            "user_id",
            "period",
            "depression",
            "anxiety",
            "energy",
            "sleep",
            "mainMood",
            "moodIntensity",
            "moodSupplementTags",
            "moodSupplementText",
            "created_at",
        ]
        extra_field_titles = [
            "记录ID",
            "用户ID",
            "记录时段",
            "抑郁",
            "焦虑",
            "精力",
            "睡眠",
            "主要情绪",
            "情绪强度",
            "情绪标签",
            "补充说明",
            "记录时间",
        ]

        def get_user_id(record):
            return record.user_id

        return build_excel_with_demographics(
            queryset, get_user_id, extra_field_order, extra_field_titles
        )

    export_selected_excel.short_description = "导出为Excel"

    def export_selected_csv(self, request, queryset):
        """导出心情日志为CSV格式（调用人口学信息导出工具）"""
        from apps.users.demographic_export import build_csv_with_demographics

        extra_field_order = [
            "id",
            "user_id",
            "period",
            "depression",
            "anxiety",
            "energy",
            "sleep",
            "mainMood",
            "moodIntensity",
            "moodSupplementTags",
            "moodSupplementText",
            "created_at",
        ]
        extra_field_titles = [
            "记录ID",
            "用户ID",
            "记录时段",
            "抑郁",
            "焦虑",
            "精力",
            "睡眠",
            "主要情绪",
            "情绪强度",
            "情绪标签",
            "补充说明",
            "记录时间",
        ]
        def get_user_id(record):
            return record.user_id

        return build_csv_with_demographics(
            queryset, get_user_id, extra_field_order, extra_field_titles
        )

    export_selected_csv.short_description = "导出为CSV"
