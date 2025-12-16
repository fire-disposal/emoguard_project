"""
认知测评流程管理后台 - 重构版本，使用统一的基础组件
"""
from django.contrib import admin
from apps.common.admin_base import TimeBasedAdmin
from apps.common.resource_configs import CognitiveAssessmentRecordResource
from apps.cognitive_flow.models import CognitiveAssessmentRecord


@admin.register(CognitiveAssessmentRecord)
class CognitiveAssessmentRecordAdmin(TimeBasedAdmin):
    """认知测评记录管理后台 - 简化版本"""
    
    resource_class = CognitiveAssessmentRecordResource
    
    # 特有配置
    list_display = (
        "id",
        "user_info",
        "score_scd",
        "score_mmse",
        "score_moca",
        "score_gad7",
        "score_phq9",
        "score_adl",
        "started_at",
        "completed_at",
        "created_at",
    )
    search_fields = ("user_id",)
    
    # 导出配置
    export_extra_fields = [
        "id", "score_scd", "score_mmse", "score_moca", "score_gad7", 
        "score_phq9", "score_adl", "started_at", "completed_at", "created_at"
    ]
    export_extra_titles = [
        "记录ID", "SCD得分", "MMSE得分", "MoCA得分", "GAD7得分", 
        "PHQ9得分", "ADL得分", "开始时间", "完成时间", "记录时间"
    ]
