"""
心情日志管理后台
"""

from django.contrib import admin
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
    started_at = fields.Field(column_name="开始作答时间", attribute="started_at")

    def dehydrate_record_date(self, obj):
        if obj.record_date:
            return obj.record_date.strftime("%Y年%m月%d日 %H点%M分%S秒")
        return ""

    def dehydrate_created_at(self, obj):
        if obj.created_at:
            return obj.created_at.strftime("%Y年%m月%d日 %H点%M分%S秒")
        return ""

    def dehydrate_started_at(self, obj):
        if obj.started_at:
            return obj.started_at.strftime("%Y年%m月%d日 %H点%M分%S秒")
        return ""

    def dehydrate(self, obj):
        data = super().dehydrate(obj)
        # 答题时长（秒），允许为空
        if obj.started_at and obj.created_at:
            delta = (obj.created_at - obj.started_at).total_seconds()
            data["答题时长"] = int(delta)
        else:
            data["答题时长"] = ""
        return data

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
            "started_at",
        ]
        export_order = fields + ["答题时长"]
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
    actions = ["export_selected_excel", "export_selected_csv", "export_user_journals_xlsx"]
    date_hierarchy = "created_at"

    def export_user_journals_xlsx(self, request, queryset):
        """
        导出所选用户的所有心情日志为xlsx（支持多用户，每个用户一份文件）。
        """
        from django.http import HttpResponse
        import openpyxl
        from openpyxl.utils import get_column_letter
        from django.utils.encoding import escape_uri_path

        user_ids = queryset.values_list("user_id", flat=True).distinct()
        for user_id in user_ids:
            records = self.model.objects.filter(user_id=user_id).order_by("created_at")
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "心情日志"
            # 表头
            headers = [
                "记录ID", "用户ID", "主观情绪", "情绪强度", "其他情绪文本", "情绪补充标签", "情绪补充说明",
                "记录日期", "创建时间", "开始作答时间", "答题时长"
            ]
            ws.append(headers)
            for obj in records:
                started_at = obj.started_at.strftime("%Y年%m月%d日 %H点%M分%S秒") if obj.started_at else ""
                created_at = obj.created_at.strftime("%Y年%m月%d日 %H点%M分%S秒") if obj.created_at else ""
                record_date = obj.record_date.strftime("%Y年%m月%d日 %H点%M分%S秒") if obj.record_date else ""
                duration = int((obj.created_at - obj.started_at).total_seconds()) if obj.started_at and obj.created_at else ""
                ws.append([
                    obj.id,
                    str(obj.user_id),
                    obj.mainMood,
                    obj.moodIntensity,
                    obj.mainMoodOther,
                    obj.moodSupplementTags,
                    obj.moodSupplementText,
                    record_date,
                    created_at,
                    started_at,
                    duration,
                ])
            # 自动列宽
            for col in ws.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except Exception:
                        pass
                ws.column_dimensions[column].width = max_length + 2
            # 响应
            filename = f"心情日志_{user_id}.xlsx"
            response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response["Content-Disposition"] = f'attachment; filename="{escape_uri_path(filename)}"'
            wb.save(response)
            return response
    export_user_journals_xlsx.short_description = "导出所选用户全部心情日志为xlsx"
    
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
