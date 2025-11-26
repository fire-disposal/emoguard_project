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
class MoodJournalAdmin(ExportActionModelAdmin):
    resource_class = MoodJournalResource
    list_display = (
        "id",
        "user_info",
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

    def user_info(self, obj):
        """显示用户信息（姓名/性别/年龄）"""
        user_info = self.get_user_info_simple(obj.user_id)
        return format_html(
            "<b>{}</b> | {} | {}岁",
            user_info.get("real_name", "未知"),
            user_info.get("gender", "未知"),
            user_info.get("age", "未知"),
        )

    user_info.short_description = "用户信息"

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

    def export_selected_excel(self, request, queryset):
        """导出心情日志为Excel格式（调用人口学信息导出工具）"""
        from apps.users.demographic_export import build_excel_with_demographics

        extra_field_order = [
            "id", "mainMood", "moodIntensity", "moodSupplementText", "record_date", "created_at"
        ]
        extra_field_titles = [
            "记录ID", "情绪名称", "情绪强度", "详细描述", "记录日期", "创建时间"
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
            "id", "mainMood", "moodIntensity", "moodSupplementText", "record_date", "created_at"
        ]
        extra_field_titles = [
            "记录ID", "情绪名称", "情绪强度", "详细描述", "记录日期", "创建时间"
        ]

        def get_user_id(record):
            return record.user_id
        
        return build_csv_with_demographics(
            queryset,get_user_id ,extra_field_order, extra_field_titles
        )

    export_selected_csv.short_description = "导出为CSV"

    def get_user_info_simple(self, user_id):
        """获取用户人口学信息（复用模块）"""
        return get_demographic_info(user_id)

    def get_gender_display(self, gender):
        """性别显示"""
        GENDER_MAP = {"male": "男", "female": "女", "other": "其他", "": "未知"}
        return GENDER_MAP.get(gender, "未知")
