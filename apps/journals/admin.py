"""
心情日志管理后台
"""

from django.contrib import admin
from apps.users.demographic_export import (
    get_demographic_info
)
from django.utils.html import format_html
from import_export.admin import ExportActionModelAdmin
from import_export import resources, fields
from apps.journals.models import MoodJournal
from apps.users.admin_mixins import BaseAdminMixin


class MoodJournalResource(resources.ModelResource):
    """心情日志导出资源（仅保留核心业务字段，人口学信息由导出模块统一处理）"""

    id = fields.Field(column_name="记录ID", attribute="id")
    user_id_display = fields.Field(column_name="用户ID", attribute="user_id")
    mainMood = fields.Field(column_name="主观情绪", attribute="mainMood")
    moodIntensity = fields.Field(column_name="情绪强度", attribute="moodIntensity")
    mainMoodOther = fields.Field(column_name="其他情绪文本", attribute="mainMoodOther")
    moodSupplementTags = fields.Field(
        column_name="情绪补充标签", attribute="moodSupplementTags"
    )
    moodSupplementText = fields.Field(
        column_name="情绪补充说明", attribute="moodSupplementText"
    )
    record_date = fields.Field(column_name="记录日期", attribute="record_date")
    created_at = fields.Field(column_name="创建时间", attribute="created_at")

    class Meta:
        model = MoodJournal
        fields = [
            "id",
            "user_id_display",
            "mainMood",
            "moodIntensity",
            "mainMoodOther",
            "moodSupplementTags",
            "moodSupplementText",
            "record_date",
            "created_at",
        ]
        export_order = fields
        skip_unchanged = True


@admin.register(MoodJournal)
class MoodJournalAdmin(BaseAdminMixin, ExportActionModelAdmin):
    resource_class = MoodJournalResource
    
    # 定义导出字段配置
    export_extra_fields = [
        "id", "mainMood", "moodIntensity", "moodSupplementText", "record_date", "created_at"
    ]
    export_extra_titles = [
        "记录ID", "情绪名称", "情绪强度", "详细描述", "记录日期", "创建时间"
    ]
    
    list_display = (
        "id",
        "user_info",  # 使用统一的user_info方法
        "mainMood",
        "moodIntensity",
        "mainMoodOther",
        "moodSupplementTags",
        "moodSupplementText",
        "record_date",
        "created_at",
    )
    list_display_links = ("id", "user_info")
    search_fields = ("user_id", "mainMood", "mainMoodOther", "moodSupplementText")
    list_filter = ("mainMood", "moodIntensity", "record_date", "created_at")
    readonly_fields = ("created_at",)
    list_select_related = ()
    list_per_page = 25
    ordering = ("-created_at",)
    actions = ["export_selected_excel", "export_selected_csv"]
    date_hierarchy = "created_at"
    
    def text_preview(self, obj):
        """文本预览"""
        if not obj.text:
            return "无描述"

        # 限制显示长度
        preview_text = obj.text[:100] + "..." if len(obj.text) > 100 else obj.text
        return format_html(
            '<div style="max-width: 400px; word-wrap: break-word;">'
            '<pre style="margin: 0; white-space: pre-wrap; font-family: inherit;">{}</pre>'
            "</div>",
            preview_text,
        )

    text_preview.short_description = "描述预览"
    
    def get_gender_display(self, gender):
        """性别显示"""
        GENDER_MAP = {"male": "男", "female": "女", "other": "其他", "": "未知"}
        return GENDER_MAP.get(gender, "未知")
