"""
心情日志管理后台 - 重构版本，使用统一的基础组件
"""
from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
import openpyxl
from django.utils.encoding import escape_uri_path
from apps.common.admin_base import TimeBasedAdmin
from apps.common.resource_configs import MoodJournalResource
from apps.journals.models import MoodJournal


@admin.register(MoodJournal)
class MoodJournalAdmin(TimeBasedAdmin):
    """心情日志管理后台 - 简化版本"""
    
    resource_class = MoodJournalResource
    
    # 特有配置
    list_display = (
        "id",
        "user_info",
        "mainMood",
        "moodIntensity",
        "mainMoodOther",
        "moodSupplementTags",
        "moodSupplementText",
        "record_date",
        "started_at",
        "created_at",
    )
    search_fields = ("user_id", "mainMood", "mainMoodOther", "moodSupplementText")
    list_filter = ("mainMood", "moodIntensity", "record_date", "created_at")
    
    # 导出配置
    export_extra_fields = [
        "id", "mainMood", "moodIntensity", "moodSupplementText", 
        "record_date", "started_at", "created_at"
    ]
    export_extra_titles = [
        "记录ID", "情绪名称", "情绪强度", "详细描述", 
        "记录日期", "开始作答时间", "创建时间"
    ]
    
    actions = ["export_selected_excel", "export_selected_csv", "export_user_journals_xlsx"]
    
    def export_user_journals_xlsx(self, request, queryset):
        """
        导出所选用户的所有心情日志为xlsx（支持多用户，每个用户一份文件）。
        保持原有功能不变
        """
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
            
            # 数据行
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
        if not obj.moodSupplementText:
            return "无描述"
        
        # 限制显示长度
        preview_text = obj.moodSupplementText[:100] + "..." if len(obj.moodSupplementText) > 100 else obj.moodSupplementText
        return format_html(
            '<div style="max-width: 400px; word-wrap: break-word;">'
            '<pre style="margin: 0; white-space: pre-wrap; font-family: inherit;">{}</pre>'
            "</div>",
            preview_text,
        )
    
    text_preview.short_description = "描述预览"
