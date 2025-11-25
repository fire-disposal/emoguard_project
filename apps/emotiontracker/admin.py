"""
情绪记录管理后台
"""
from django.contrib import admin
from import_export.admin import ExportActionModelAdmin
from import_export import resources, fields
from apps.emotiontracker.models import EmotionRecord
from apps.users.models import User


class EmotionRecordResource(resources.ModelResource):
    """情绪记录导出资源"""
    id = fields.Field(column_name='记录ID', attribute='id')
    user_id_display = fields.Field(column_name='用户ID', attribute='user_id')
    period = fields.Field(column_name='时段', attribute='period')
    depression = fields.Field(column_name='抑郁得分', attribute='depression')
    anxiety = fields.Field(column_name='焦虑得分', attribute='anxiety')
    energy = fields.Field(column_name='精力得分', attribute='energy')
    sleep = fields.Field(column_name='睡眠得分', attribute='sleep')
    mainMood = fields.Field(column_name='主要情绪', attribute='mainMood')
    moodIntensity = fields.Field(column_name='情绪强度', attribute='moodIntensity')
    moodSupplementTags = fields.Field(column_name='情绪标签', attribute='moodSupplementTags')
    moodSupplementText = fields.Field(column_name='补充说明', attribute='moodSupplementText')
    created_at = fields.Field(column_name='记录时间', attribute='created_at')

    class Meta:
        model = EmotionRecord
        fields = [
            'id', 'user_id_display',
            'period', 'depression', 'anxiety', 'energy', 'sleep',
            'mainMood', 'moodIntensity', 'moodSupplementTags', 'moodSupplementText',
            'created_at'
        ]
        export_order = fields
        skip_unchanged = True
    


@admin.register(EmotionRecord)
class EmotionRecordAdmin(ExportActionModelAdmin):
    resource_class = EmotionRecordResource
    list_display = (
        'id', 'user_id', 'period', 'depression', 'anxiety', 'energy', 'sleep',
        'mainMood', 'moodIntensity', 'moodSupplementTags', 'moodSupplementText', 'created_at'
    )
    search_fields = ('user_id', 'mainMood', 'period')
    list_filter = ('period', 'mainMood', 'moodIntensity', 'created_at')
    readonly_fields = ('created_at',)
    list_per_page = 25
    ordering = ('-created_at',)
    actions = ['export_selected_excel', 'export_selected_csv']
    date_hierarchy = 'created_at'

    def export_selected_excel(self, request, queryset):
        from apps.scales.admin.demographic_export import build_excel_with_demographics
        extra_field_order = [
            "id", "user_id", "period", "depression", "anxiety", "energy", "sleep",
            "mainMood", "moodIntensity", "moodSupplementTags", "moodSupplementText", "created_at"
        ]
        extra_field_titles = [
            "记录ID", "用户ID", "时段", "抑郁得分", "焦虑得分", "精力得分", "睡眠得分",
            "主要情绪", "情绪强度", "情绪标签", "补充说明", "记录时间"
        ]
        def get_user_id(record):
            return record.user_id
        return build_excel_with_demographics(queryset, get_user_id, extra_field_order, extra_field_titles)
    export_selected_excel.short_description = '导出为Excel'

    def export_selected_csv(self, request, queryset):
        from apps.scales.admin.demographic_export import build_csv_with_demographics
        extra_field_order = [
            "id", "user_id", "period", "depression", "anxiety", "energy", "sleep",
            "mainMood", "moodIntensity", "moodSupplementTags", "moodSupplementText", "created_at"
        ]
        extra_field_titles = [
            "记录ID", "用户ID", "时段", "抑郁得分", "焦虑得分", "精力得分", "睡眠得分",
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