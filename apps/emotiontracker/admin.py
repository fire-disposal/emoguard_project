"""
情绪记录管理后台
"""

from django.contrib import admin
from import_export.admin import ExportActionModelAdmin
from import_export import resources, fields
from apps.emotiontracker.models import EmotionRecord
from apps.users.admin_mixins import BaseAdminMixin


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
class EmotionRecordAdmin(BaseAdminMixin, ExportActionModelAdmin):
    resource_class = EmotionRecordResource
    
    # 定义导出字段配置
    export_extra_fields = [
        "id",
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
    export_extra_titles = [
        "记录ID",
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
    
    list_display = (
        "id",
        "user_info",  # 使用统一的user_info方法
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
