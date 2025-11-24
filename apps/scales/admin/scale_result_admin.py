"""
量表结果管理 - ScaleResult 的后台管理
"""
from django.contrib import admin
from django.utils.html import format_html
from django.template.response import TemplateResponse
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from import_export.admin import ExportActionModelAdmin
from apps.scales.models import ScaleResult
from import_export import resources, fields
from apps.scales.admin.filters import ScaleFilter, StatusFilter

import json
import logging


logger = logging.getLogger(__name__)


class ScaleResultResource(resources.ModelResource):
    """量表结果导出资源 - 原生风格，保持数据库原样输出"""

    # 基础信息 - 直接映射数据库字段
    id = fields.Field(column_name='ID', attribute='id')
    user_id = fields.Field(column_name='用户ID', attribute='user_id')
    scale_config_id = fields.Field(column_name='量表配置ID', attribute='scale_config_id')
    selected_options = fields.Field(column_name='选项答案', attribute='selected_options')
    conclusion = fields.Field(column_name='结论摘要', attribute='conclusion')
    duration_ms = fields.Field(column_name='答题时长(毫秒)', attribute='duration_ms')
    started_at = fields.Field(column_name='开始时间', attribute='started_at')
    completed_at = fields.Field(column_name='完成时间', attribute='completed_at')
    status = fields.Field(column_name='状态', attribute='status')
    analysis = fields.Field(column_name='分析结果', attribute='analysis')
    created_at = fields.Field(column_name='创建时间', attribute='created_at')
    updated_at = fields.Field(column_name='更新时间', attribute='updated_at')
    
    class Meta:
        model = ScaleResult
        fields = [
            'id', 'user_id', 'scale_config_id', 'selected_options', 'conclusion',
            'duration_ms', 'started_at', 'completed_at', 'status', 'analysis',
            'created_at', 'updated_at'
        ]
        export_order = fields
        skip_unchanged = True
        report_skipped = True
    
    def dehydrate_selected_options(self, result):
        """保持选项答案原样输出"""
        return result.selected_options if result.selected_options else []
    
    def dehydrate_analysis(self, result):
        """保持分析结果原样输出"""
        return result.analysis if result.analysis else {}


@admin.register(ScaleResult)
class ScaleResultAdmin(ExportActionModelAdmin):
    resource_class = ScaleResultResource
    list_display = ('id', 'user_id', 'scale_config', 'status', 'duration_formatted', 'created_at')
    list_display_links = ('id', 'user_id')
    search_fields = ('user_id', 'scale_config__name', 'scale_config__code', 'scale_config__type')
    list_filter = ('status', 'scale_config__type', ScaleFilter, StatusFilter, 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'analysis_preview', 'quick_stats')
    list_select_related = ('scale_config',)
    list_per_page = 25
    ordering = ('-created_at',)
    actions = [
        'export_selected_excel_flat',
        'export_selected_csv_flat'
    ]
    date_hierarchy = 'created_at'
    
    export_filename = '量表结果导出'
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
    
    def get_queryset(self, request):
        """优化查询性能"""
        return super().get_queryset(request).select_related('scale_config')
    
    def quick_stats(self, obj):
        """快速统计信息"""
        if not isinstance(obj.analysis, dict):
            return '无统计数据'
        try:
            preview_data = {k: obj.analysis.get(k) for k in ['score', 'level', 'is_abnormal', 'risk_level']}
            preview_data = {k: v for k, v in preview_data.items() if v is not None}
            return format_html(
                '<pre class="analysis-preview">{}</pre>',
                json.dumps(preview_data, ensure_ascii=False, indent=2)
            )
        except Exception as e:
            logger.error(f"生成快速统计失败: {str(e)}")
            return '统计错误'
    quick_stats.short_description = '快速统计'
    
    def duration_formatted(self, obj):
        """格式化显示答题时长"""
        return format_duration(obj.duration_ms)
    duration_formatted.short_description = '答题时长'
    
    
    def analysis_preview(self, obj):
        """分析结果预览"""
        if not isinstance(obj.analysis, dict):
            return "无分析数据"
        try:
            preview_data = {
                'score': obj.analysis.get('score'),
                'level': obj.analysis.get('level'),
                'max_score': obj.analysis.get('max_score'),
                'is_abnormal': obj.analysis.get('is_abnormal'),
                'recommendations': obj.analysis.get('recommendations', [])[:2]
            }
            preview_data = {k: v for k, v in preview_data.items() if v is not None}
            formatted = json.dumps(preview_data, ensure_ascii=False, indent=2)
            return format_html('<pre class="analysis-preview">{}</pre>', formatted)
        except Exception as e:
            logger.error(f"预览分析结果失败: {str(e)}")
            return "分析数据格式错误"
    analysis_preview.short_description = '分析预览'
    
    # 批量操作
    def export_selected_excel_flat(self, request, queryset):
        """导出为Excel（人口学信息+展平题目分数，题目文本）"""
        from apps.scales.admin.demographic_export import build_excel_with_demographics
        from apps.scales.services.scale_result_service import ScaleResultService
        def get_user_id(record):
            return record.user_id
        # 取第一个对象的题目结构
        if queryset:
            titles, _ = ScaleResultService.flatten_scale_result(queryset[0], with_question_info=True)
            extra_field_order = [
                "id", "conclusion", "duration_ms", "started_at", "completed_at",
                "status", "analysis", "created_at", "updated_at"
            ] + [f"q_{i}" for i in range(len(titles))]
            extra_field_titles = [
                "ID", "结论摘要", "答题时长(毫秒)", "开始时间", "完成时间",
                "状态", "分析结果", "创建时间", "更新时间"
            ] + titles
        else:
            extra_field_order = []
            extra_field_titles = []
        def build_row(user_info, extra_fields, extra_field_order):
            record = extra_fields.get('record', None)
            if record is None:
                return [""] * len(extra_field_order)
            row = [
                str(getattr(record, "id", "")),
                str(getattr(record, "conclusion", "")),
                str(getattr(record, "duration_ms", "")),
                str(getattr(record, "started_at", "")),
                str(getattr(record, "completed_at", "")),
                str(getattr(record, "status", "")),
                str(getattr(record, "analysis", "")),
                str(getattr(record, "created_at", "")),
                str(getattr(record, "updated_at", ""))
            ]
            _, values = ScaleResultService.flatten_scale_result(record, with_question_info=True)
            row += [str(v) if not isinstance(v, (int, float, type(None))) else v for v in values]
            return row
        import apps.scales.admin.demographic_export as dexp
        dexp.build_row_with_demographics = build_row
        return build_excel_with_demographics(queryset, get_user_id, extra_field_order, extra_field_titles)
    export_selected_excel_flat.short_description = '导出Excel（展平题目）'

    def export_selected_excel_plain(self, request, queryset):
        """导出为Excel（题目展平，不带题目信息）"""
        from apps.scales.admin.demographic_export import build_excel_with_demographics
        from apps.scales.services.scale_result_service import ScaleResultService
        def get_user_id(record):
            return record.user_id
        if queryset:
            titles, _ = ScaleResultService.flatten_scale_result(queryset[0], with_question_info=False)
            extra_field_order = [
                "id", "scale_config_id", "conclusion", "duration_ms",
                "started_at", "completed_at", "status", "analysis", "created_at", "updated_at", "user_snapshot"
            ] + [f"q_{i}" for i in range(len(titles))]
            extra_field_titles = [
                "ID", "量表配置ID", "结论摘要", "答题时长(毫秒)",
                "开始时间", "完成时间", "状态", "分析结果", "创建时间", "更新时间", "用户信息快照"
            ] + titles
        else:
            extra_field_order = []
            extra_field_titles = []
        def build_row(user_info, extra_fields, extra_field_order):
            record = extra_fields.get('record', None)
            if record is None:
                record = extra_fields if hasattr(extra_fields, 'scale_config_id') else user_info
            if record is None or not hasattr(record, 'scale_config_id'):
                return [""] * len(extra_field_order)
            row = [getattr(record, k, "") for k in extra_field_order if not k.startswith("q_")]
            _, values = ScaleResultService.flatten_scale_result(record, with_question_info=False)
            row += values
            row = [str(v) if not isinstance(v, (int, float, type(None))) else v for v in row]
            return row
        import apps.scales.admin.demographic_export as dexp
        dexp.build_row_with_demographics = build_row
        return build_excel_with_demographics(queryset, get_user_id, extra_field_order, extra_field_titles)
    export_selected_excel_plain.short_description = '导出Excel（题目展平，不带题目信息）'

    def export_selected_csv_flat(self, request, queryset):
        """导出为CSV（人口学信息+展平题目分数，题目文本）"""
        from apps.scales.admin.demographic_export import build_csv_with_demographics
        from apps.scales.services.scale_result_service import ScaleResultService
        def get_user_id(record):
            return record.user_id
        if queryset:
            titles, _ = ScaleResultService.flatten_scale_result(queryset[0], with_question_info=True)
            extra_field_order = [
                "id", "conclusion", "duration_ms", "started_at", "completed_at",
                "status", "analysis", "created_at", "updated_at"
            ] + [f"q_{i}" for i in range(len(titles))]
            extra_field_titles = [
                "ID", "结论摘要", "答题时长(毫秒)", "开始时间", "完成时间",
                "状态", "分析结果", "创建时间", "更新时间"
            ] + titles
        else:
            extra_field_order = []
            extra_field_titles = []
        def build_row(user_info, extra_fields, extra_field_order):
            record = extra_fields.get('record', None)
            if record is None:
                return [""] * len(extra_field_order)
            row = [
                str(getattr(record, "id", "")),
                str(getattr(record, "conclusion", "")),
                str(getattr(record, "duration_ms", "")),
                str(getattr(record, "started_at", "")),
                str(getattr(record, "completed_at", "")),
                str(getattr(record, "status", "")),
                str(getattr(record, "analysis", "")),
                str(getattr(record, "created_at", "")),
                str(getattr(record, "updated_at", ""))
            ]
            _, values = ScaleResultService.flatten_scale_result(record, with_question_info=True)
            row += [str(v) if not isinstance(v, (int, float, type(None))) else v for v in values]
            return row
        import apps.scales.admin.demographic_export as dexp
        dexp.build_row_with_demographics = build_row
        return build_csv_with_demographics(queryset, get_user_id, extra_field_order, extra_field_titles)
    export_selected_csv_flat.short_description = '导出CSV（展平题目）'

    def export_selected_csv_plain(self, request, queryset):
        """导出为CSV（题目展平，不带题目信息）"""
        from apps.scales.admin.demographic_export import build_csv_with_demographics
        from apps.scales.services.scale_result_service import ScaleResultService
        def get_user_id(record):
            return record.user_id
        if queryset:
            titles, _ = ScaleResultService.flatten_scale_result(queryset[0], with_question_info=False)
            extra_field_order = [
                "id", "scale_config_id", "conclusion", "duration_ms",
                "started_at", "completed_at", "status", "analysis", "created_at", "updated_at", "user_snapshot"
            ] + [f"q_{i}" for i in range(len(titles))]
            extra_field_titles = [
                "ID", "量表配置ID", "结论摘要", "答题时长(毫秒)",
                "开始时间", "完成时间", "状态", "分析结果", "创建时间", "更新时间", "用户信息快照"
            ] + titles
        else:
            extra_field_order = []
            extra_field_titles = []
        def build_row(user_info, extra_fields, extra_field_order):
            record = extra_fields.get('record', None)
            row = [getattr(record, k, "") for k in extra_field_order if not k.startswith("q_")]
            _, values = ScaleResultService.flatten_scale_result(record, with_question_info=False)
            row += values
            return row
        import apps.scales.admin.demographic_export as dexp
        dexp.build_row_with_demographics = build_row
        return build_csv_with_demographics(queryset, get_user_id, extra_field_order, extra_field_titles)
    export_selected_csv_plain.short_description = '导出CSV（题目展平，不带题目信息）'
    
    def export_selected_csv(self, request, queryset):
        """导出为CSV格式（人口学信息封装，用户信息快照字段原样导出）"""
        from apps.scales.admin.demographic_export import build_csv_with_demographics
        extra_field_order = [
            "id", "scale_config_id", "selected_options", "conclusion", "duration_ms",
            "started_at", "completed_at", "status", "analysis", "created_at", "updated_at", "user_snapshot"
        ]
        extra_field_titles = [
            "ID", "量表配置ID", "选项答案", "结论摘要", "答题时长(毫秒)",
            "开始时间", "完成时间", "状态", "分析结果", "创建时间", "更新时间", "用户信息快照"
        ]
        def get_user_id(record):
            return record.user_id
        return build_csv_with_demographics(queryset, get_user_id, extra_field_order, extra_field_titles)
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

def format_duration(duration_ms):
    """格式化时长显示"""
    if not duration_ms:
        return "0秒"
    seconds = duration_ms // 1000
    if seconds < 60:
        return f"{seconds}秒"
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}分{remaining_seconds}秒"