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
    started_at = fields.Field(column_name="开始作答时间", attribute="started_at")

    def dehydrate_id(self, obj):
        return str(obj.id)

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
            "started_at",
        ]
        export_order = fields + ["答题时长"]
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
        "user_info",
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
    actions = ["export_selected_excel", "export_selected_csv", "export_user_records_xlsx"]
    date_hierarchy = "created_at"

    def export_user_records_xlsx(self, request, queryset):
        """
        导出所选用户的所有情绪记录为xlsx（支持多用户，每个用户一份文件）。
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
            ws.title = "情绪记录"
            # 表头
            headers = [
                "记录ID", "用户ID", "时段", "抑郁得分", "焦虑得分", "精力得分", "睡眠得分",
                "主要情绪", "情绪强度", "情绪标签", "补充说明", "记录时间", "开始作答时间", "答题时长"
            ]
            ws.append(headers)
            for obj in records:
                started_at = obj.started_at.strftime("%Y年%m月%d日 %H点%M分%S秒") if obj.started_at else ""
                created_at = obj.created_at.strftime("%Y年%m月%d日 %H点%M分%S秒") if obj.created_at else ""
                duration = int((obj.created_at - obj.started_at).total_seconds()) if obj.started_at and obj.created_at else ""
                ws.append([
                    obj.id,
                    str(obj.user_id),
                    obj.period,
                    obj.depression,
                    obj.anxiety,
                    obj.energy,
                    obj.sleep,
                    obj.mainMood,
                    obj.moodIntensity,
                    obj.moodSupplementTags,
                    obj.moodSupplementText,
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
            filename = f"情绪记录_{user_id}.xlsx"
            response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response["Content-Disposition"] = f'attachment; filename="{escape_uri_path(filename)}"'
            wb.save(response)
            return response
    export_user_records_xlsx.short_description = "导出所选用户全部情绪记录为xlsx"
