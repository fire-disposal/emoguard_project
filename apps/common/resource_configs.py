"""
各模块的资源类配置 - 使用统一的基础资源类
"""
from import_export import fields
from apps.common.admin_base import BaseResource
from apps.emotiontracker.models import EmotionRecord
from apps.cognitive_flow.models import CognitiveAssessmentRecord
from apps.journals.models import MoodJournal
from apps.feedback.models import Feedback
from apps.reports.models import HealthReport
from apps.scales.models import ScaleResult


class EmotionRecordResource(BaseResource):
    """情绪记录导出资源"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 添加情绪记录特有字段
        self.fields.update({
            'period': fields.Field(column_name="时段", attribute="period"),
            'depression': fields.Field(column_name="抑郁得分", attribute="depression"),
            'anxiety': fields.Field(column_name="焦虑得分", attribute="anxiety"),
            'energy': fields.Field(column_name="精力得分", attribute="energy"),
            'sleep': fields.Field(column_name="睡眠得分", attribute="sleep"),
            'mainMood': fields.Field(column_name="主要情绪", attribute="mainMood"),
            'moodIntensity': fields.Field(column_name="情绪强度", attribute="moodIntensity"),
            'moodSupplementTags': fields.Field(column_name="情绪标签", attribute="moodSupplementTags"),
            'moodSupplementText': fields.Field(column_name="补充说明", attribute="moodSupplementText"),
        })
    
    class Meta:
        model = EmotionRecord
        skip_unchanged = True


class CognitiveAssessmentRecordResource(BaseResource):
    """认知测评记录导出资源"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 添加认知测评特有字段
        self.fields.update({
            'score_scd': fields.Field(column_name="SCD得分", attribute="score_scd"),
            'score_mmse': fields.Field(column_name="MMSE得分", attribute="score_mmse"),
            'score_moca': fields.Field(column_name="MoCA得分", attribute="score_moca"),
            'score_gad7': fields.Field(column_name="GAD7得分", attribute="score_gad7"),
            'score_phq9': fields.Field(column_name="PHQ9得分", attribute="score_phq9"),
            'score_adl': fields.Field(column_name="ADL得分", attribute="score_adl"),
        })
    
    class Meta:
        model = CognitiveAssessmentRecord
        skip_unchanged = True


class MoodJournalResource(BaseResource):
    """心情日志导出资源"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 添加心情日志特有字段
        self.fields.update({
            'mainMood': fields.Field(column_name="主观情绪", attribute="mainMood"),
            'moodIntensity': fields.Field(column_name="情绪强度", attribute="moodIntensity"),
            'mainMoodOther': fields.Field(column_name="其他情绪文本", attribute="mainMoodOther"),
            'moodSupplementTags': fields.Field(column_name="情绪补充标签", attribute="moodSupplementTags"),
            'moodSupplementText': fields.Field(column_name="情绪补充说明", attribute="moodSupplementText"),
        })
    
    class Meta:
        model = MoodJournal
        skip_unchanged = True


class FeedbackResource(BaseResource):
    """用户反馈导出资源"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 添加反馈特有字段
        self.fields.update({
            'rating': fields.Field(column_name="评分", attribute="rating"),
            'content': fields.Field(column_name="反馈内容", attribute="content"),
            'is_processed': fields.Field(column_name="已处理", attribute="is_processed"),
        })
    
    class Meta:
        model = Feedback
        skip_unchanged = True


class HealthReportResource(BaseResource):
    """健康报告导出资源"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 添加健康报告特有字段
        self.fields.update({
            'assessment_id': fields.Field(column_name="测评记录ID", attribute="assessment_id"),
            'report_type': fields.Field(column_name="报告类型", attribute="report_type"),
            'overall_risk': fields.Field(column_name="整体风险", attribute="overall_risk"),
        })
    
    class Meta:
        model = HealthReport
        skip_unchanged = True


class ScaleResultResource(BaseResource):
    """量表结果导出资源"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 添加量表结果特有字段
        self.fields.update({
            'scale_code': fields.Field(column_name="量表编码", attribute="scale_code"),
            'score': fields.Field(column_name="得分", attribute="score"),
        })
    
    class Meta:
        model = ScaleResult
        skip_unchanged = True