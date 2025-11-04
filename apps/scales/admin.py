from django.contrib import admin
from django import forms
from .models import ScaleConfig, ScaleResult
from django.utils.html import format_html
from import_export.admin import ExportActionModelAdmin
import json


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
        if obj and obj.questions:
            try:
                formatted = json.dumps(obj.questions, ensure_ascii=False, indent=2)
                # 使用 format_html 标记生成的 HTML 是安全的
                # 注意：这里 formatted 变量包含的是纯文本 JSON，所以我们直接将 HTML 结构作为安全字符串返回
                return format_html('<pre style="background: #f5f5f5; padding: 10px; border-radius: 4px;">{}</pre>', formatted)
            except:
                return str(obj.questions)
        return '暂无数据'
    
    preview_questions.short_description = '问题列表预览'

@admin.register(ScaleResult)
class ScaleResultAdmin(ExportActionModelAdmin):
    list_display = ('id', 'user_id', 'scale_config', 'status', 'duration_ms', 'started_at', 'completed_at', 'created_at', 'updated_at')
    search_fields = ('user_id', 'scale_config__name')
    list_filter = ('status', 'scale_config')
    readonly_fields = ('created_at', 'updated_at')