"""
智能测评管理 - SmartAssessmentRecord 的后台管理
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.http import HttpResponse
from apps.scales.models import SmartAssessmentRecord
from apps.scales.admin.filters import AssessmentStatusFilter
from apps.scales.admin.utils import (
    get_user_info, format_user_info_html, format_status_badge, 
    format_progress_bar, format_duration, format_risk_assessment
)
import csv
import logging


logger = logging.getLogger(__name__)


@admin.register(SmartAssessmentRecord)
class SmartAssessmentRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_info', 'status_display', 'progress_display', 'scale_count_display', 'data_consistency_display', 'created_at', 'duration_display')
    list_display_links = ('id', 'user_info')
    list_filter = ('status', AssessmentStatusFilter, 'created_at')
    search_fields = ('user_id', 'id')
    readonly_fields = ('started_at', 'created_at', 'updated_at', 'final_result_preview', 'results_summary', 'quick_overview', 'data_consistency_detail')
    list_select_related = True
    list_per_page = 20
    ordering = ('-created_at',)
    actions = ['mark_as_completed', 'export_assessment_summary', 'validate_data_consistency']
    date_hierarchy = 'created_at'
        
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request)
    
    def user_info(self, obj):
        """显示用户信息（增强版）"""
        user_info = get_user_info(obj.user_id)
        return format_user_info_html(user_info, show_full=True)
    user_info.short_description = '用户信息'
    
    def scale_count_display(self, obj):
        """量表数量显示"""
        completed_count = len(obj.scale_scores)
        total_count = len(obj.scale_responses)
        
        if obj.status == 'completed':
            return format_html(
                '<span style="color: #27ae60; font-weight: bold;">{} / {}</span>',
                completed_count, total_count
            )
        elif obj.status == 'in_progress':
            return format_html(
                '<span style="color: #f39c12;">{} / {}</span>',
                completed_count, total_count
            )
        else:
            return format_html(
                '<span style="color: #95a5a6;">{} / {}</span>',
                completed_count, total_count
            )
    scale_count_display.short_description = '量表进度'
    
    def status_display(self, obj):
        """状态显示（带颜色）"""
        return format_status_badge(obj.status, status_type='assessment')
    status_display.short_description = '状态'
    
    def progress_display(self, obj):
        """进度显示"""
        if obj.status == 'completed':
            return format_html(
                '<div style="text-align: center;">'
                '<div style="background-color: #27ae60; color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px;">'
                '100%'
                '</div>'
                '</div>'
            )
        
        # 获取已完成的量表数量
        completed_scales = len(obj.scale_scores)
        total_scales = max(len(obj.scale_responses), 1)  # 至少为1避免除零
        
        return format_progress_bar(completed_scales, total_scales, width=100)
    progress_display.short_description = '进度'
    
    def duration_display(self, obj):
        """时长显示（格式化）"""
        if obj.status == 'completed' and obj.completed_at:
            duration = obj.get_total_duration()
            return format_duration(duration)
        else:
            return "-"
    duration_display.short_description = '总时长'
    
    def quick_overview(self, obj):
        """快速概览（主题友好）"""
        if not obj.final_result or not isinstance(obj.final_result, dict):
            return '无概览数据'
        
        try:
            risk_data = format_risk_assessment(obj.final_result)
            
            return format_html(
                '<div class="assessment-overview">'
                '<h4 class="overview-title">📊 测评概览</h4>'
                '<div class="overview-grid">'
                '<div class="overview-item"><strong>结论:</strong> <span class="risk-level {}">{}</span></div>'
                '<div class="overview-item"><strong>风险等级:</strong> <span class="risk-level {}">{}</span></div>'
                '<div class="overview-item"><strong>异常项目:</strong> {} 项</div>'
                '<div class="overview-item"><strong>总分:</strong> {} 分</div>'
                '</div>'
                '</div>',
                risk_data['risk_level'].replace('风险', ''), risk_data['conclusion'],
                risk_data['risk_level'].replace('风险', ''), risk_data['risk_level'],
                risk_data['abnormal_count'], risk_data['total_score']
            )
        except Exception as e:
            logger.error(f"生成快速概览失败: {str(e)}")
            return '概览数据错误'
    quick_overview.short_description = '快速概览'
    
    def data_consistency_display(self, obj):
        """数据一致性状态显示"""
        consistency_errors = obj.validate_data_consistency()
        
        if not consistency_errors:
            return format_html(
                '<span class="status-badge status-completed" style="background-color: #27ae60;">'
                '✓ 一致</span>'
            )
        else:
            error_count = len(consistency_errors)
            return format_html(
                '<span class="status-badge status-abnormal" style="background-color: #e74c3c; cursor: pointer;" '
                'title="{}">'
                '⚠ {} 个问题</span>',
                '；'.join(consistency_errors),
                error_count
            )
    data_consistency_display.short_description = '数据一致性'
    
    def data_consistency_detail(self, obj):
        """数据一致性详细信息"""
        consistency_errors = obj.validate_data_consistency()
        
        if not consistency_errors:
            return format_html(
                '<div class="consistency-status" style="color: #27ae60; padding: 10px; background-color: #d4edda; '
                'border: 1px solid #c3e6cb; border-radius: 4px;">'
                '✅ 数据一致性验证通过'
                '</div>'
            )
        else:
            error_list = '<br>'.join(f'• {error}' for error in consistency_errors)
            return format_html(
                '<div class="consistency-errors" style="color: #721c24; padding: 10px; background-color: #f8d7da; '
                'border: 1px solid #f5c6cb; border-radius: 4px;">'
                '<strong>❌ 发现以下数据一致性问题：</strong><br><br>{}'
                '</div>',
                error_list
            )
    data_consistency_detail.short_description = '数据一致性详情'
    
    def final_result_preview(self, obj):
        """预览最终结果"""
        if not obj.final_result or not isinstance(obj.final_result, dict):
            return "无最终结果"
        
        try:
            conclusion = obj.final_result.get('conclusion', '未知结论')
            risk_level = obj.final_result.get('risk_level', '未知风险')
            
            # 构建预览内容
            preview_parts = [f"结论：{conclusion}（{risk_level}）"]
            
            recommendations = obj.final_result.get('recommendations', [])
            if recommendations:
                preview_parts.append("建议：")
                for i, rec in enumerate(recommendations[:3]):  # 只显示前3条建议
                    preview_parts.append(f"  {i+1}. {rec}")
            
            return format_html(
                '<div class="result-preview">{}</div>',
                '<br>'.join(preview_parts)
            )
        except Exception as e:
            logger.error(f"预览最终结果失败: {str(e)}")
            return "最终结果数据格式错误"
    final_result_preview.short_description = '最终结果'
    
    def results_summary(self, obj):
        """显示结果摘要（主题友好）"""
        try:
            # 获取该测评的所有量表结果
            results = obj.scale_results.all().select_related('scale_config')
            
            if not results.exists():
                return "暂无量表结果"
            
            summary_parts = []
            for result in results:
                scale_name = result.scale_config.name
                analysis = result.analysis or {}
                score = analysis.get('score', 'N/A')
                level = analysis.get('level', 'N/A')
                summary_parts.append(f"{scale_name}：{score}分（{level}）")
            
            return format_html(
                '<div class="results-summary">{}</div>',
                '<br>'.join(summary_parts)
            )
        except Exception as e:
            logger.error(f"获取结果摘要失败: {str(e)}")
            return "获取结果摘要失败"
    results_summary.short_description = '量表结果摘要'
    
    # 批量操作
    def mark_as_completed(self, request, queryset):
        """标记为已完成"""
        updated = queryset.filter(status='in_progress').update(
            status='completed',
            completed_at=timezone.now()
        )
        self.message_user(request, f'已将 {updated} 个测评标记为已完成')
    mark_as_completed.short_description = '标记为已完成'
    
    def export_assessment_summary(self, request, queryset):
        """导出测评摘要"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="测评摘要_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['测评ID', '用户ID', '用户姓名', '状态', '量表数量', '异常项目数', '总分', '风险等级', '结论', '创建时间', '完成时间'])
        
        for assessment in queryset.select_related():
            user_info = get_user_info(assessment.user_id)
            final_result = assessment.final_result or {}
            
            writer.writerow([
                assessment.id,
                str(assessment.user_id),
                user_info.get('real_name', '未知'),
                assessment.get_status_display(),
                len(assessment.scale_scores),
                final_result.get('abnormal_count', 0),
                final_result.get('total_score', 0),
                final_result.get('risk_level', '未知'),
                final_result.get('conclusion', '未知'),
                assessment.created_at.strftime('%Y-%m-%d %H:%M'),
                assessment.completed_at.strftime('%Y-%m-%d %H:%M') if assessment.completed_at else '未完成'
            ])
        
        return response
    export_assessment_summary.short_description = '导出测评摘要'
    
    def validate_data_consistency(self, request, queryset):
        """验证数据一致性"""
        total_checked = 0
        total_errors = 0
        error_details = []
        
        for assessment in queryset:
            total_checked += 1
            errors = assessment.validate_data_consistency()
            if errors:
                total_errors += len(errors)
                error_details.append(f"测评ID {assessment.id}: {'；'.join(errors)}")
        
        if total_errors == 0:
            self.message_user(request, f'✅ 已验证 {total_checked} 个测评，数据一致性良好', level='success')
        else:
            error_msg = f'⚠️ 已验证 {total_checked} 个测评，发现 {total_errors} 个数据一致性问题：'
            for detail in error_details[:5]:  # 只显示前5个详细信息
                error_msg += f'<br>• {detail}'
            if len(error_details) > 5:
                error_msg += f'<br>• ... 还有 {len(error_details) - 5} 个问题'
            self.message_user(request, error_msg, level='warning')
    validate_data_consistency.short_description = '验证数据一致性'