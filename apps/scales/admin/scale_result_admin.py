"""
量表结果管理 - ScaleResult 的后台管理
"""
from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from import_export.admin import ExportActionModelAdmin
from apps.scales.models import ScaleResult
from apps.scales.admin.resources import ScaleResultResource
from apps.scales.admin.filters import UserFilter, ScaleFilter, StatusFilter
from apps.scales.admin.utils import (
    get_user_info, format_user_info_html, format_duration
)
import json
import logging


logger = logging.getLogger(__name__)


@admin.register(ScaleResult)
class ScaleResultAdmin(ExportActionModelAdmin):
    resource_class = ScaleResultResource
    list_display = ('id', 'user_info', 'scale_config', 'status', 'duration_formatted', 'score_display', 'created_at')
    list_display_links = ('id', 'user_info')
    search_fields = ('user_id', 'scale_config__name', 'scale_config__code', 'scale_config__type')
    list_filter = ('status', 'scale_config__type', ScaleFilter, UserFilter, StatusFilter, 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'score_display', 'analysis_preview', 'quick_stats')
    list_select_related = ('scale_config',)
    list_per_page = 25
    ordering = ('-created_at',)
    actions = ['export_selected_excel', 'export_selected_csv', 'mark_as_reviewed', 'bulk_delete_results']
    date_hierarchy = 'created_at'
    
    # 导出配置
    # export_formats = ['xlsx', 'csv']  # 错误写法，已注释
    export_filename = '量表结果导出'
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
    
    def get_queryset(self, request):
        """优化查询性能"""
        return super().get_queryset(request).select_related('scale_config')
    
    def quick_stats(self, obj):
        """快速统计信息（主题友好）"""
        if not obj.analysis or not isinstance(obj.analysis, dict):
            return '无统计数据'
        
        try:
            score = obj.analysis.get('score', 'N/A')
            max_score = obj.analysis.get('max_score', 'N/A')
            level = obj.analysis.get('level', 'N/A')
            is_abnormal = obj.analysis.get('is_abnormal', False)
            
            abnormal_class = 'status-abnormal' if is_abnormal else 'status-normal'
            abnormal_text = '异常' if is_abnormal else '正常'
            
            return format_html(
                '<div class="quick-stats">'
                '<div class="stat-item">得分: <strong>{}</strong> / {}</div>'
                '<div class="stat-item">等级: <strong>{}</strong></div>'
                '<div class="stat-item {}">状态: <strong>{}</strong></div>'
                '</div>',
                score, max_score, level, abnormal_class, abnormal_text
            )
        except Exception as e:
            logger.error(f"生成快速统计失败: {str(e)}")
            return '统计错误'
    quick_stats.short_description = '快速统计'
    
    def user_info(self, obj):
        """显示用户信息"""
        user_info = get_user_info(obj.user_id)
        return format_user_info_html(user_info, show_full=False)
    user_info.short_description = '用户信息'
    
    def duration_formatted(self, obj):
        """格式化显示答题时长"""
        return format_duration(obj.duration_ms)
    duration_formatted.short_description = '答题时长'
    
    def score_display(self, obj):
        """显示评分信息（主题友好）"""
        if not obj.analysis or not isinstance(obj.analysis, dict):
            return "无数据"
        
        score = obj.analysis.get('score', 'N/A')
        level = obj.analysis.get('level', 'N/A')
        
        # 根据是否有异常状态显示不同信息
        if 'is_abnormal' in obj.analysis:
            abnormal_class = 'score-abnormal' if obj.analysis['is_abnormal'] else 'score-normal'
            abnormal_status = "异常" if obj.analysis['is_abnormal'] else "正常"
            return format_html(
                '<div class="score-display">'
                '<div class="score-value">{}分</div>'
                '<div class="score-level">{}</div>'
                '<div class="{}">{}</div>'
                '</div>',
                score, level, abnormal_class, abnormal_status
            )
        else:
            return format_html(
                '<div class="score-display">'
                '<div class="score-value">{}分</div>'
                '<div class="score-level">{}</div>'
                '</div>',
                score, level
            )
    score_display.short_description = '评分信息'
    
    def analysis_preview(self, obj):
        """预览分析结果（主题友好）"""
        if not obj.analysis or not isinstance(obj.analysis, dict):
            return "无分析数据"
        
        try:
            # 显示关键信息
            preview_data = {
                'score': obj.analysis.get('score'),
                'level': obj.analysis.get('level'),
                'max_score': obj.analysis.get('max_score'),
                'is_abnormal': obj.analysis.get('is_abnormal'),
                'recommendations': obj.analysis.get('recommendations', [])[:2]  # 只显示前2条建议
            }
            
            # 移除None值
            preview_data = {k: v for k, v in preview_data.items() if v is not None}
            
            formatted = json.dumps(preview_data, ensure_ascii=False, indent=2)
            return format_html(
                '<pre class="analysis-preview">{}</pre>',
                formatted
            )
        except Exception as e:
            logger.error(f"预览分析结果失败: {str(e)}")
            return "分析数据格式错误"
    analysis_preview.short_description = '分析预览'
    
    # 批量操作
    def export_selected_excel(self, request, queryset):
        """导出为Excel格式"""
        import openpyxl
        from openpyxl.styles import Font, PatternFill
        from datetime import datetime
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "量表结果"
        
        # 设置标题行
        headers = ['ID', '用户ID', '用户姓名', '年龄', '性别', '学历', '量表名称', '量表代码', '得分', '等级', '状态', '答题时长(分)', '完成时间']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell.font = Font(color="FFFFFF", bold=True)
        
        # 填充数据
        for row, result in enumerate(queryset.select_related('scale_config'), 2):
            user_info = get_user_info(result.user_id)
            analysis = result.analysis or {}
            
            ws.cell(row=row, column=1, value=result.id)
            ws.cell(row=row, column=2, value=str(result.user_id))
            ws.cell(row=row, column=3, value=user_info.get('real_name', '未知'))
            ws.cell(row=row, column=4, value=user_info.get('age', '未知'))
            ws.cell(row=row, column=5, value=user_info.get('gender', '未知'))
            ws.cell(row=row, column=6, value=user_info.get('education', '未知'))
            ws.cell(row=row, column=7, value=result.scale_config.name)
            ws.cell(row=row, column=8, value=result.scale_config.code)
            ws.cell(row=row, column=9, value=analysis.get('score', 'N/A'))
            ws.cell(row=row, column=10, value=analysis.get('level', 'N/A'))
            ws.cell(row=row, column=11, value='异常' if analysis.get('is_abnormal') else '正常')
            ws.cell(row=row, column=12, value=round(result.duration_ms / 60000, 1) if result.duration_ms else 0)
            ws.cell(row=row, column=13, value=result.completed_at.strftime('%Y-%m-%d %H:%M'))
        
        # 调整列宽
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    
                    pass
            adjusted_width = min(max_length + 2, 20)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="量表结果_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
        
        wb.save(response)
        return response
    export_selected_excel.short_description = '导出为Excel'
    
    def export_selected_csv(self, request, queryset):
        """导出为CSV格式"""
        import csv
        from datetime import datetime
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="量表结果_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', '用户ID', '用户姓名', '年龄', '性别', '学历', '量表名称', '量表代码', '得分', '等级', '状态', '答题时长(分)', '完成时间'])
        
        for result in queryset.select_related('scale_config'):
            user_info = get_user_info(result.user_id)
            analysis = result.analysis or {}
            writer.writerow([
                result.id,
                str(result.user_id),
                user_info.get('real_name', '未知'),
                user_info.get('age', '未知'),
                user_info.get('gender', '未知'),
                user_info.get('education', '未知'),
                result.scale_config.name,
                result.scale_config.code,
                analysis.get('score', 'N/A'),
                analysis.get('level', 'N/A'),
                '异常' if analysis.get('is_abnormal') else '正常',
                round(result.duration_ms / 60000, 1) if result.duration_ms else 0,
                result.completed_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response
    export_selected_csv.short_description = '导出为CSV'
    
    def mark_as_reviewed(self, request, queryset):
        """标记为已审核"""
        # 可以添加审核逻辑，比如添加审核标记到analysis中
        updated = queryset.count()
        self.message_user(request, f'已标记 {updated} 条记录为已审核')
    mark_as_reviewed.short_description = '标记为已审核'
    
    def bulk_delete_results(self, request, queryset):
        """批量删除结果（带确认）"""
        if request.POST.get('post'):
            # 确认删除
            count = queryset.count()
            queryset.delete()
            self.message_user(request, f'已删除 {count} 条记录')
        else:
            # 显示确认页面
            context = {
                'title': '确认批量删除',
                'queryset': queryset,
                'action_checkbox_name': ACTION_CHECKBOX_NAME,
                'action': 'bulk_delete_results',
                'opts': self.model._meta,
            }
            return TemplateResponse(request, 'admin/bulk_delete_confirmation.html', context)
    bulk_delete_results.short_description = '批量删除所选记录'