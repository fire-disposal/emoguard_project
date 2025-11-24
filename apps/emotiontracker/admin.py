"""
情绪记录管理后台
"""
from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ExportActionModelAdmin
from import_export import resources, fields
from apps.emotiontracker.models import EmotionRecord
from apps.users.models import User
import json


class EmotionRecordResource(resources.ModelResource):
    """情绪记录导出资源"""
    
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
    period = fields.Field(column_name='时段', attribute='period')
    depression = fields.Field(column_name='抑郁得分', attribute='depression')
    anxiety = fields.Field(column_name='焦虑得分', attribute='anxiety')
    energy = fields.Field(column_name='精力得分', attribute='energy')
    sleep = fields.Field(column_name='睡眠得分', attribute='sleep')
    main_mood = fields.Field(column_name='主要情绪', attribute='main_mood')
    mood_intensity = fields.Field(column_name='情绪强度', attribute='mood_intensity')
    mood_supplement_tags = fields.Field(column_name='情绪标签', attribute='mood_supplement_tags')
    mood_supplement_text = fields.Field(column_name='补充说明', attribute='mood_supplement_text')
    created_at = fields.Field(column_name='记录时间', attribute='created_at')
    
    class Meta:
        model = EmotionRecord
        fields = [
            'id', 'user_id_display', 'user_real_name', 'user_gender', 'user_age',
            'period', 'depression', 'anxiety', 'energy', 'sleep',
            'main_mood', 'mood_intensity', 'mood_supplement_tags', 'mood_supplement_text',
            'created_at'
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
    
    def dehydrate_mood_supplement_tags(self, record):
        """情绪标签显示"""
        tags = record.mood_supplement_tags or []
        if isinstance(tags, list):
            tag_map = {
                'body': '身体不适',
                'family': '家庭事务',
                'memory': '记忆困扰',
                'sleep': '睡眠不好',
                'work': '工作/学习压力',
                'other': '其他'
            }
            return '; '.join([tag_map.get(tag, tag) for tag in tags])
        return str(tags)
    
    def dehydrate_main_mood(self, record):
        """主要情绪显示"""
        mood_map = {
            'happy': '快乐/愉快',
            'calm': '平静/放松',
            'sad': '难过/悲伤',
            'anxious': '焦虑/担心',
            'angry': '易怒/烦躁',
            'tired': '疲惫/无力',
            'other': '其他'
        }
        return mood_map.get(record.main_mood, record.main_mood or '未知')


@admin.register(EmotionRecord)
class EmotionRecordAdmin(ExportActionModelAdmin):
    resource_class = EmotionRecordResource
    list_display = ('id', 'user_info', 'period', 'main_mood_display', 'moodIntensity', 'created_at')
    list_display_links = ('id', 'user_info')
    search_fields = ('user_id', 'main_mood', 'period')
    list_filter = ('period', 'mainMood', 'moodIntensity', 'created_at')
    readonly_fields = ('created_at', 'analysis_preview')
    list_select_related = ()
    list_per_page = 25
    ordering = ('-created_at',)
    actions = ['export_selected_excel', 'export_selected_csv']
    date_hierarchy = 'created_at'
    
    def user_info(self, obj):
        """显示用户人口学信息（复用 demographic_export 工具）"""
        from apps.scales.admin.demographic_export import get_demographic_info
        user_info = get_demographic_info(obj.user_id)
        # 格式化展示
        return format_html(
            "<b>{}</b> | {} | {}岁",
            user_info.get("real_name", "未知"),
            user_info.get("gender", "未知"),
            user_info.get("age", "未知"),
        )
    user_info.short_description = '用户信息'
    
    def main_mood_display(self, obj):
        """显示主要情绪"""
        mood_map = {
            'happy': '快乐',
            'calm': '平静',
            'sad': '悲伤',
            'anxious': '焦虑',
            'angry': '烦躁',
            'tired': '疲惫',
            'other': '其他'
        }
        mood_text = mood_map.get(obj.main_mood, obj.main_mood or '未知')
        
        # 添加情绪强度显示
        intensity_map = {1: '轻微', 2: '中等', 3: '明显'}
        intensity_text = intensity_map.get(obj.mood_intensity, '未知')
        
        return format_html(
            '<div style="display: flex; flex-direction: column;">'
            '<span style="font-weight: 600; color: #1890ff;">{}</span>'
            '<span style="font-size: 12px; color: #999;">强度: {}</span>'
            '</div>',
            mood_text, intensity_text
        )
    main_mood_display.short_description = '情绪状态'
    
    def analysis_preview(self, obj):
        """预览分析结果"""
        data = {
            '抑郁得分': obj.depression,
            '焦虑得分': obj.anxiety,
            '精力得分': obj.energy,
            '睡眠得分': obj.sleep,
            '主要情绪': obj.main_mood,
            '情绪强度': obj.mood_intensity,
            '情绪标签': obj.mood_supplement_tags,
            '补充说明': obj.mood_supplement_text
        }
        
        # 移除None值
        data = {k: v for k, v in data.items() if v is not None}
        
        formatted = json.dumps(data, ensure_ascii=False, indent=2)
        return format_html('<pre class="analysis-preview">{}</pre>', formatted)
    analysis_preview.short_description = '数据预览'
    
    def export_selected_excel(self, request, queryset):
        """导出情绪记录为Excel格式（调用人口学信息导出工具）"""
        from apps.scales.admin.demographic_export import build_excel_with_demographics

        extra_field_order = [
            "id", "period", "depression", "anxiety", "energy", "sleep",
            "main_mood", "mood_intensity", "mood_supplement_tags", "mood_supplement_text", "created_at"
        ]
        extra_field_titles = [
            "记录ID", "时段", "抑郁得分", "焦虑得分", "精力得分", "睡眠得分",
            "主要情绪", "情绪强度", "情绪标签", "补充说明", "记录时间"
        ]
        def get_user_id(record):
            return record.user_id
        return build_excel_with_demographics(queryset, get_user_id, extra_field_order, extra_field_titles)
    export_selected_excel.short_description = '导出为Excel'
    
    def export_selected_csv(self, request, queryset):
        """导出情绪记录为CSV格式（调用人口学信息导出工具）"""
        from apps.scales.admin.demographic_export import build_csv_with_demographics

        extra_field_order = [
            "id", "period", "depression", "anxiety", "energy", "sleep",
            "main_mood", "mood_intensity", "mood_supplement_tags", "mood_supplement_text", "created_at"
        ]
        extra_field_titles = [
            "记录ID", "时段", "抑郁得分", "焦虑得分", "精力得分", "睡眠得分",
            "主要情绪", "情绪强度", "情绪标签", "补充说明", "记录时间"
        ]
        def get_user_id(record):
            return record.user_id
        return build_csv_with_demographics(queryset, get_user_id, extra_field_order, extra_field_titles)
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
    
    def get_period_display(self, period):
        """时段显示"""
        PERIOD_MAP = {
            'morning': '早间',
            'evening': '晚间'
        }
        return PERIOD_MAP.get(period, period or '未知')
    
    def get_mood_display(self, mood):
        """情绪显示"""
        mood_map = {
            'happy': '快乐',
            'calm': '平静',
            'sad': '悲伤',
            'anxious': '焦虑',
            'angry': '烦躁',
            'tired': '疲惫',
            'other': '其他'
        }
        return mood_map.get(mood, mood or '未知')
    
    def get_intensity_display(self, intensity):
        """强度显示"""
        intensity_map = {1: '轻微', 2: '中等', 3: '明显'}
        return intensity_map.get(intensity, '未知')
    
    def get_tags_display(self, tags):
        """标签显示"""
        if not tags or not isinstance(tags, list):
            return ''
        
        tag_map = {
            'body': '身体不适',
            'family': '家庭事务',
            'memory': '记忆困扰',
            'sleep': '睡眠不好',
            'work': '工作/学习压力',
            'other': '其他'
        }
        return '; '.join([tag_map.get(tag, tag) for tag in tags])