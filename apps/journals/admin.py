"""
心情日志管理后台
"""
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from import_export.admin import ExportActionModelAdmin
from import_export import resources, fields
from apps.journals.models import MoodJournal
from apps.users.models import User
import csv
from datetime import datetime


class MoodJournalResource(resources.ModelResource):
    """心情日志导出资源"""
    
    id = fields.Field(column_name='记录ID', attribute='id')
    user_id_display = fields.Field(column_name='用户ID', attribute='user_id')
    user_real_name = fields.Field(
        column_name='用户姓名',
        attribute='user_id',
        widget=fields.widgets.ForeignKeyWidget(User, 'real_name')
    )
    user_gender = fields.Field(
        column_name='性别',
        attribute='user_id',
        widget=fields.widgets.ForeignKeyWidget(User, 'gender')
    )
    user_age = fields.Field(
        column_name='年龄',
        attribute='user_id',
        widget=fields.widgets.ForeignKeyWidget(User, 'age')
    )
    mainMood = fields.Field(column_name='主观情绪', attribute='mainMood')
    moodIntensity = fields.Field(column_name='情绪强度', attribute='moodIntensity')
    mainMoodOther = fields.Field(column_name='其他情绪文本', attribute='mainMoodOther')
    moodSupplementTags = fields.Field(column_name='情绪补充标签', attribute='moodSupplementTags')
    moodSupplementText = fields.Field(column_name='情绪补充说明', attribute='moodSupplementText')
    record_date = fields.Field(column_name='记录日期', attribute='record_date')
    created_at = fields.Field(column_name='创建时间', attribute='created_at')
    
    class Meta:
        model = MoodJournal
        fields = [
            'id', 'user_id_display', 'user_real_name', 'user_gender', 'user_age',
            'mainMood', 'moodIntensity', 'mainMoodOther', 'moodSupplementTags', 'moodSupplementText', 'record_date', 'created_at'
        ]
        export_order = fields
        skip_unchanged = True
    
    def dehydrate_user_gender(self, record):
        """性别显示"""
        GENDER_MAP = {
            'male': '男',
            'female': '女',
            'other': '其他',
            '': '未知'
        }
        try:
            user = User.objects.get(id=record.user_id)
            return GENDER_MAP.get(user.gender, '未知')
        except User.DoesNotExist:
            return '用户不存在'
    
    def dehydrate_user_age(self, record):
        """年龄显示"""
        try:
            user = User.objects.get(id=record.user_id)
            return str(user.age) if user.age else '未知'
        except User.DoesNotExist:
            return '未知'


@admin.register(MoodJournal)
class MoodJournalAdmin(ExportActionModelAdmin):
    resource_class = MoodJournalResource
    list_display = ('id', 'user_info', 'mainMood', 'moodIntensity', 'mainMoodOther', 'moodSupplementTags', 'moodSupplementText', 'record_date', 'created_at')
    list_display_links = ('id', 'user_info')
    search_fields = ('user_id', 'mainMood', 'mainMoodOther', 'moodSupplementText')
    list_filter = ('mainMood', 'moodIntensity', 'record_date', 'created_at')
    readonly_fields = ('created_at',)
    list_select_related = ()
    list_per_page = 25
    ordering = ('-created_at',)
    actions = ['export_selected_excel', 'export_selected_csv']
    date_hierarchy = 'created_at'
    
    def user_info(self, obj):
        """显示用户信息"""
        from apps.scales.admin.utils import get_user_info, format_user_info_html
        user_info = get_user_info(obj.user_id)
        return format_user_info_html(user_info, show_full=False)
    user_info.short_description = '用户信息'
    
    def text_preview(self, obj):
        """文本预览"""
        if not obj.text:
            return "无描述"
        
        # 限制显示长度
        preview_text = obj.text[:100] + '...' if len(obj.text) > 100 else obj.text
        return format_html(
            '<div style="max-width: 400px; word-wrap: break-word;">'
            '<pre style="margin: 0; white-space: pre-wrap; font-family: inherit;">{}</pre>'
            '</div>',
            preview_text
        )
    text_preview.short_description = '描述预览'
    
    def export_selected_excel(self, request, queryset):
        """导出心情日志为Excel格式"""
        import openpyxl
        from openpyxl.styles import Font, PatternFill
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "心情日志"
        
        # 设置标题行
        headers = ['记录ID', '用户ID', '用户姓名', '性别', '年龄', 
                  '情绪名称', '情绪分数', '详细描述', '记录日期', '创建时间']
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell.font = Font(color="FFFFFF", bold=True)
        
        # 填充数据
        for row, record in enumerate(queryset, 2):
            user_info = self.get_user_info_simple(record.user_id)
            
            ws.cell(row=row, column=1, value=record.id)
            ws.cell(row=row, column=2, value=str(record.user_id))
            ws.cell(row=row, column=3, value=user_info.get('real_name', '未知'))
            ws.cell(row=row, column=4, value=user_info.get('gender', '未知'))
            ws.cell(row=row, column=5, value=user_info.get('age', '未知'))
            ws.cell(row=row, column=6, value=record.mood_name or '未知')
            ws.cell(row=row, column=7, value=record.mood_score or 'N/A')
            ws.cell(row=row, column=8, value=record.text or '')
            ws.cell(row=row, column=9, value=record.record_date.strftime('%Y-%m-%d'))
            ws.cell(row=row, column=10, value=record.created_at.strftime('%Y-%m-%d %H:%M'))
        
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
            adjusted_width = min(max_length + 2, 30)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="心情日志_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
        
        wb.save(response)
        return response
    export_selected_excel.short_description = '导出为Excel'
    
    def export_selected_csv(self, request, queryset):
        """导出心情日志为CSV格式"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="心情日志_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['记录ID', '用户ID', '用户姓名', '性别', '年龄', 
                        '情绪名称', '情绪分数', '详细描述', '记录日期', '创建时间'])
        
        for record in queryset:
            user_info = self.get_user_info_simple(record.user_id)
            writer.writerow([
                record.id,
                str(record.user_id),
                user_info.get('real_name', '未知'),
                user_info.get('gender', '未知'),
                user_info.get('age', '未知'),
                record.mood_name or '未知',
                record.mood_score or 'N/A',
                record.text or '',
                record.record_date.strftime('%Y-%m-%d'),
                record.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response
    export_selected_csv.short_description = '导出为CSV'
    
    def get_user_info_simple(self, user_id):
        """获取用户简单信息"""
        try:
            user = User.objects.get(id=user_id)
            return {
                'real_name': user.real_name or '未知',
                'gender': self.get_gender_display(user.gender),
                'age': user.age or '未知'
            }
        except User.DoesNotExist:
            return {
                'real_name': '用户不存在',
                'gender': '未知',
                'age': '未知'
            }
    
    def get_gender_display(self, gender):
        """性别显示"""
        GENDER_MAP = {
            'male': '男',
            'female': '女',
            'other': '其他',
            '': '未知'
        }
        return GENDER_MAP.get(gender, '未知')