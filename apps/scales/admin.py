"""
量表管理后台 - 优化版本，增强安全性和用户体验
"""
from django.contrib import admin
from django import forms
from django.utils.html import format_html
from import_export.admin import ExportActionModelAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
import json
import logging

from .models import ScaleConfig, ScaleResult, SmartAssessmentRecord
from apps.users.models import User

class UserFilter(admin.SimpleListFilter):
    """按用户筛选"""
    title = '用户筛选'
    parameter_name = 'user_filter'
    
    def lookups(self, request, model_admin):
        # 获取有评估记录的用户
        user_ids = ScaleResult.objects.values_list('user_id', flat=True).distinct()[:50]
        users = []
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                display_name = f"{user.real_name} ({user.age}岁)" if user.real_name else str(user_id)[:8]
                users.append((str(user_id), display_name))
            except User.DoesNotExist:
                users.append((str(user_id), f"用户{str(user_id)[:8]}"))
        return sorted(users, key=lambda x: x[1])
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user_id=self.value())
        return queryset


class ScaleFilter(admin.SimpleListFilter):
    """按量表筛选"""
    title = '量表筛选'
    parameter_name = 'scale_filter'
    
    def lookups(self, request, model_admin):
        # 获取有记录的量表
        scales = ScaleConfig.objects.filter(
            results__isnull=False
        ).distinct().order_by('name')[:30]
        
        return [(str(scale.id), f"{scale.name} ({scale.code})") for scale in scales]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(scale_config_id=self.value())
        return queryset


logger = logging.getLogger(__name__)


class ScaleConfigAdminForm(forms.ModelForm):
    """自定义表单，优化 YAML 编辑体验"""
    
    class Meta:
        model = ScaleConfig
        fields = '__all__'
        widgets = {
            'yaml_config': forms.Textarea(attrs={
                'rows': 25,
                'cols': 80,
                'style': 'font-family: monospace; font-size: 13px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px;',
                'placeholder': '''示例 YAML 格式：
name: 量表名称
code: SCALE_CODE
version: "1.0"
description: 量表描述
type: 量表类型
status: active
questions:
  - id: 1
    question: 问题内容
    options:
      - text: 选项A
        value: 0
      - text: 选项B
        value: 1'''
            }),
        }
        help_texts = {
            'yaml_config': '编辑此 YAML 配置会自动更新下方所有字段。推荐：直接编辑 YAML 配置，保存时会自动解析并填充所有字段。',
            'name': '量表名称（如果编辑了 YAML，此字段会被自动覆盖）',
            'code': '量表唯一代码（如果编辑了 YAML，此字段会被自动覆盖）',
            'version': '版本号（如果编辑了 YAML，此字段会被自动覆盖）',
            'description': '量表描述（如果编辑了 YAML，此字段会被自动覆盖）',
            'type': '量表类型（如果编辑了 YAML，此字段会被自动覆盖）',
            'status': '量表状态（如果编辑了 YAML，此字段会被自动覆盖）',
        }


@admin.register(ScaleConfig)
class ScaleConfigAdmin(admin.ModelAdmin):
    form = ScaleConfigAdminForm
    list_display = ('id', 'name', 'code', 'version', 'type', 'status', 'created_at', 'updated_at')
    search_fields = ('name', 'code', 'description')
    list_filter = ('status', 'type')
    readonly_fields = ('created_at', 'updated_at', 'preview_questions')
    
    fieldsets = (
        ('基础信息（可直接编辑）', {
            'fields': ('name', 'code', 'version', 'type', 'description', 'status','created_at','updated_at'),
            'description': '基本信息，编辑后会更新至yaml中'
        }),
        ('YAML 配置（主要编辑区）', {
            'fields': ('yaml_config',),
            'description': '推荐：直接编辑 YAML 配置，保存时会自动解析并解析问卷问题'
        }),
        ('问题浏览', {
            'fields': ('questions', 'preview_questions'),
            'classes': ('collapse',),
        })
    )
    
    def preview_questions(self, obj):
        """预览解析后的问题列表（格式化显示）"""
        if not obj or not obj.questions:
            return '暂无数据'
        
        try:
            # 验证questions格式
            if not isinstance(obj.questions, list):
                logger.warning(f"量表{obj.id}的问题数据格式不正确")
                return '问题数据格式错误'
            
            # 格式化JSON显示
            formatted = json.dumps(obj.questions, ensure_ascii=False, indent=2)
            return format_html(
                '<pre style="background: #f8f9fa; padding: 12px; border-radius: 4px; font-family: monospace; font-size: 12px; max-height: 300px; overflow-y: auto;">{}</pre>',
                formatted
            )
        except (TypeError, ValueError) as e:
            logger.error(f"预览量表{obj.id}问题失败: {str(e)}")
            return '问题数据解析失败'
        except Exception as e:
            logger.error(f"预览量表{obj.id}问题时发生未知错误: {str(e)}")
            return '预览失败'
    
    preview_questions.short_description = '问题预览'


class ScaleResultResource(resources.ModelResource):
    """量表结果导出资源 - 包含用户个人信息"""
    
    # 用户基本信息
    user_real_name = fields.Field(
        column_name='用户姓名',
        attribute='user__real_name',
        widget=ForeignKeyWidget(User, 'real_name')
    )
    user_gender = fields.Field(
        column_name='性别',
        attribute='user__gender',
        widget=ForeignKeyWidget(User, 'gender')
    )
    user_age = fields.Field(
        column_name='年龄',
        attribute='user__age',
        widget=ForeignKeyWidget(User, 'age')
    )
    user_education = fields.Field(
        column_name='学历',
        attribute='user__education',
        widget=ForeignKeyWidget(User, 'education')
    )
    user_province = fields.Field(
        column_name='省份',
        attribute='user__province',
        widget=ForeignKeyWidget(User, 'province')
    )
    user_city = fields.Field(
        column_name='城市',
        attribute='user__city',
        widget=ForeignKeyWidget(User, 'city')
    )
    user_district = fields.Field(
        column_name='区县',
        attribute='user__district',
        widget=ForeignKeyWidget(User, 'district')
    )
    user_phone = fields.Field(
        column_name='手机号',
        attribute='user__phone',
        widget=ForeignKeyWidget(User, 'phone')
    )
    
    # 量表基本信息
    scale_name = fields.Field(
        column_name='量表名称',
        attribute='scale_config__name',
        widget=ForeignKeyWidget(ScaleConfig, 'name')
    )
    scale_code = fields.Field(
        column_name='量表代码',
        attribute='scale_config__code',
        widget=ForeignKeyWidget(ScaleConfig, 'code')
    )
    scale_type = fields.Field(
        column_name='量表类型',
        attribute='scale_config__type',
        widget=ForeignKeyWidget(ScaleConfig, 'type')
    )
    
    # 结果信息
    score = fields.Field(column_name='得分', attribute='analysis')
    max_score = fields.Field(column_name='满分', attribute='analysis')
    level = fields.Field(column_name='等级', attribute='analysis')
    is_abnormal = fields.Field(column_name='是否异常', attribute='analysis')
    recommendations = fields.Field(column_name='建议', attribute='analysis')
    
    # 时间信息
    duration_seconds = fields.Field(column_name='答题时长(秒)', attribute='duration_ms')
    started_at = fields.Field(column_name='开始时间', attribute='started_at')
    completed_at = fields.Field(column_name='完成时间', attribute='completed_at')
    created_at = fields.Field(column_name='创建时间', attribute='created_at')
    
    class Meta:
        model = ScaleResult
        fields = [
            'id', 'user_id', 'user_real_name', 'user_gender', 'user_age', 'user_education',
            'user_province', 'user_city', 'user_district', 'user_phone',
            'scale_name', 'scale_code', 'scale_type',
            'score', 'max_score', 'level', 'is_abnormal', 'recommendations',
            'duration_seconds', 'started_at', 'completed_at', 'created_at'
        ]
        export_order = fields
    
    def dehydrate_score(self, result):
        """提取得分"""
        return result.analysis.get('score', '') if result.analysis else ''
    
    def dehydrate_max_score(self, result):
        """提取满分"""
        return result.analysis.get('max_score', '') if result.analysis else ''
    
    def dehydrate_level(self, result):
        """提取等级"""
        return result.analysis.get('level', '') if result.analysis else ''
    
    def dehydrate_is_abnormal(self, result):
        """提取是否异常"""
        abnormal = result.analysis.get('is_abnormal', '') if result.analysis else ''
        return '是' if abnormal else '否' if abnormal != '' else ''
    
    def dehydrate_recommendations(self, result):
        """提取建议"""
        recommendations = result.analysis.get('recommendations', []) if result.analysis else []
        return '; '.join(recommendations) if recommendations else ''
    
    def dehydrate_duration_seconds(self, result):
        """转换时长为秒"""
        return result.duration_ms // 1000 if result.duration_ms else 0


@admin.register(ScaleResult)
class ScaleResultAdmin(ExportActionModelAdmin):
    resource_class = ScaleResultResource
    list_display = ('id', 'user_info', 'scale_config', 'status', 'duration_formatted', 'score_display', 'created_at')
    search_fields = ('user_id', 'scale_config__name', 'scale_config__code')
    list_filter = ('status', 'scale_config__type', ScaleFilter, UserFilter, 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'score_display', 'analysis_preview')
    list_select_related = ('scale_config',)
    list_per_page = 20
    
    def get_queryset(self, request):
        """优化查询性能"""
        return super().get_queryset(request).select_related('scale_config')
    
    def user_info(self, obj):
        """显示用户信息"""
        try:
            from apps.users.models import User
            user = User.objects.get(id=obj.user_id)
            return format_html(
                '<div style="font-size: 12px;">'
                '<div>{}</div>'
                '<div style="color: #666;">{}岁 {}</div>'
                '<div style="color: #999;">{}</div>'
                '</div>',
                user.real_name or str(obj.user_id)[:8] + '...',
                user.age or '未知',
                user.get_gender_display() if user.gender else '未知',
                user.education or '未知学历'
            )
        except User.DoesNotExist:
            return str(obj.user_id)[:8] + '...'
    user_info.short_description = '用户信息'
    
    def duration_formatted(self, obj):
        """格式化显示答题时长"""
        if not obj.duration_ms:
            return "0秒"
        
        seconds = obj.duration_ms // 1000
        if seconds < 60:
            return f"{seconds}秒"
        else:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{minutes}分{remaining_seconds}秒"
    duration_formatted.short_description = '答题时长'
    
    def score_display(self, obj):
        """显示评分信息"""
        if not obj.analysis or not isinstance(obj.analysis, dict):
            return "无数据"
        
        score = obj.analysis.get('score', 'N/A')
        level = obj.analysis.get('level', 'N/A')
        
        # 根据是否有异常状态显示不同信息
        if 'is_abnormal' in obj.analysis:
            abnormal_status = "异常" if obj.analysis['is_abnormal'] else "正常"
            return f"{score}分 | {level} | {abnormal_status}"
        else:
            return f"{score}分 | {level}"
    score_display.short_description = '评分信息'
    
    def analysis_preview(self, obj):
        """预览分析结果"""
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
                '<pre style="background: #f8f9fa; padding: 8px; border-radius: 4px; font-family: monospace; font-size: 11px; max-height: 200px; overflow-y: auto;">{}</pre>',
                formatted
            )
        except Exception as e:
            logger.error(f"预览分析结果失败: {str(e)}")
            return "分析数据格式错误"
    analysis_preview.short_description = '分析预览'


@admin.register(SmartAssessmentRecord)
class SmartAssessmentRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'strategy', 'status', 'created_at', 'completed_at')
    list_filter = ('status', 'strategy', 'created_at')
    search_fields = ('user_id', 'id')
    readonly_fields = ('started_at', 'created_at', 'updated_at', 'final_result_preview', 'results_summary')
    list_select_related = True
    list_per_page = 15
    
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
                '<div style="background: #f8f9fa; padding: 12px; border-radius: 4px; font-size: 12px; max-height: 200px; overflow-y: auto;">{}</div>',
                '<br>'.join(preview_parts)
            )
        except Exception as e:
            logger.error(f"预览最终结果失败: {str(e)}")
            return "最终结果数据格式错误"
    final_result_preview.short_description = '最终结果'
    
    def results_summary(self, obj):
        """显示结果摘要"""
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
                '<div style="background: #e9ecef; padding: 8px; border-radius: 4px; font-size: 11px;">{}</div>',
                '<br>'.join(summary_parts)
            )
        except Exception as e:
            logger.error(f"获取结果摘要失败: {str(e)}")
            return "获取结果摘要失败"
    results_summary.short_description = '量表结果摘要'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user_id', 'strategy', 'status', 'current_scale_index'),
            'description': '智能测评的基本信息'
        }),
        ('最终结果', {
            'fields': ('final_result_preview',),
            'description': '智能测评的最终结果'
        }),
        ('结果摘要', {
            'fields': ('results_summary',),
            'description': '该测评下所有量表的结果摘要',
            'classes': ('collapse',),
        }),
        ('时间信息', {
            'fields': ('started_at', 'completed_at', 'created_at', 'updated_at'),
            'description': '智能测评的时间记录'
        }),
    )