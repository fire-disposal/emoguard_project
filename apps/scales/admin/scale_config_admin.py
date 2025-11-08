"""
量表配置管理 - ScaleConfig 的后台管理
"""
from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.db import models
from apps.scales.models import ScaleConfig
import json
import logging


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
    list_display = ('id', 'name', 'code', 'version', 'type', 'status', 'usage_count', 'created_at', 'updated_at')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'code', 'description', 'type')
    list_filter = ('status', 'type', 'created_at')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at', 'preview_questions', 'usage_count', 'quick_actions')
    ordering = ('-created_at',)
    list_per_page = 20
    actions = ['activate_scales', 'deactivate_scales', 'duplicate_scale']
    
    fieldsets = (
        ('基础信息（可直接编辑）', {
            'fields': ('name', 'code', 'version', 'type', 'description', 'status', 'quick_actions'),
            'description': '基本信息，编辑后会更新至yaml中'
        }),
        ('YAML 配置（主要编辑区）', {
            'fields': ('yaml_config',),
            'description': '推荐：直接编辑 YAML 配置，保存时会自动解析并解析问卷问题'
        }),
        ('统计信息', {
            'fields': ('usage_count', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
        ('问题浏览', {
            'fields': ('questions', 'preview_questions'),
            'classes': ('collapse',),
        })
    )
    
    def get_queryset(self, request):
        """优化查询，添加使用统计"""
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            usage_count=models.Count('results')
        )
        return queryset
    
    def usage_count(self, obj):
        """显示使用次数（主题友好）"""
        count = getattr(obj, 'usage_count', 0)
        if count > 0:
            return format_html(
                '<span class="usage-count active">{} 次</span>',
                count
            )
        return format_html(
            '<span class="usage-count inactive">未使用</span>'
        )
    usage_count.short_description = '使用次数'
    usage_count.admin_order_field = 'usage_count'
    
    def quick_actions(self, obj):
        """快速操作按钮（主题友好）"""
        if not obj.pk:
            return '-'
        
        return format_html(
            '<div class="quick-actions">'
            '<a class="btn btn-preview" href="{}">🔍 预览量表</a>'
            '<a class="btn btn-results" href="{}">📊 查看结果</a>'
            '</div>',
            f'/admin/scales/scaleconfig/{obj.id}/change/#questions',
            f'/admin/scales/scaleresult/?scale_config__id={obj.id}'
        )
    quick_actions.short_description = '快速操作'
    quick_actions.allow_tags = True
    
    def activate_scales(self, request, queryset):
        """批量启用量表"""
        updated = queryset.update(status='active')
        self.message_user(request, f'已启用 {updated} 个量表')
    activate_scales.short_description = '批量启用所选量表'
    
    def deactivate_scales(self, request, queryset):
        """批量停用量表"""
        updated = queryset.update(status='draft')
        self.message_user(request, f'已停用 {updated} 个量表')
    deactivate_scales.short_description = '批量停用所选量表'
    
    def duplicate_scale(self, request, queryset):
        """复制量表配置"""
        for obj in queryset:
            new_obj = ScaleConfig.objects.get(pk=obj.pk)
            new_obj.pk = None
            new_obj.code = f"{obj.code}_copy_{obj.id}"
            new_obj.name = f"{obj.name} (副本)"
            new_obj.status = 'draft'
            new_obj.save()
        self.message_user(request, f'已复制 {queryset.count()} 个量表')
    duplicate_scale.short_description = '复制所选量表'
    
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
                '<pre class="json-preview">{}</pre>',
                formatted
            )
        except (TypeError, ValueError) as e:
            logger.error(f"预览量表{obj.id}问题失败: {str(e)}")
            return '问题数据解析失败'
        except Exception as e:
            logger.error(f"预览量表{obj.id}问题时发生未知错误: {str(e)}")
            return '预览失败'
    
    preview_questions.short_description = '问题预览'