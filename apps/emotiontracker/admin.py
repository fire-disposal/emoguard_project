"""
情绪记录管理后台 - 重构版本，使用统一的基础组件
"""
from django.contrib import admin
from django.http import HttpResponse
import openpyxl
from django.utils.encoding import escape_uri_path
from apps.common.admin_base import TimeBasedAdmin
from apps.common.resource_configs import EmotionRecordResource
from apps.emotiontracker.models import EmotionRecord


@admin.register(EmotionRecord)
class EmotionRecordAdmin(TimeBasedAdmin):
    """情绪记录管理后台 - 简化版本"""
    
    resource_class = EmotionRecordResource
    
    # 特有配置
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
        "started_at",
        "created_at",
    )
    search_fields = ("user_id", "mainMood", "period")
    list_filter = ("period", "mainMood", "moodIntensity", "created_at")
    
    # 导出配置
    export_extra_fields = [
        "id", "period", "depression", "anxiety", "energy", "sleep",
        "mainMood", "moodIntensity", "moodSupplementTags", 
        "moodSupplementText", "started_at", "created_at"
    ]
    export_extra_titles = [
        "记录ID", "记录时段", "抑郁", "焦虑", "精力", "睡眠",
        "主要情绪", "情绪强度", "情绪标签", "补充说明", 
        "开始作答时间", "记录时间"
    ]
    
    actions = ["export_selected_excel", "export_selected_csv", "export_user_records_xlsx"]
    
    def export_user_records_xlsx(self, request, queryset):
        """
        导出所选用户的所有情绪记录为xlsx（支持多用户，每个用户一份文件）。
        保持原有功能不变
        """
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
            
            # 数据行
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
