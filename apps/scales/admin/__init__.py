"""
量表管理后台 - 模块化设计
"""
from .scale_config_admin import ScaleConfigAdmin
from .scale_result_admin import ScaleResultAdmin
from .smart_assessment_admin import SmartAssessmentRecordAdmin

# 导出资源类
from .resources import ScaleResultResource, SmartAssessmentResource

# 过滤器类
from .filters import UserFilter, ScaleFilter, StatusFilter, AssessmentStatusFilter

# 工具函数
from .utils import (
    get_user_info, format_user_info_html, format_status_badge,
    format_progress_bar, format_duration, format_phone_privacy,
    get_risk_color, format_risk_assessment
)

__all__ = [
    # Admin 类
    'ScaleConfigAdmin', 'ScaleResultAdmin', 'SmartAssessmentRecordAdmin',
    # 资源类
    'ScaleResultResource', 'SmartAssessmentResource',
    # 过滤器类
    'UserFilter', 'ScaleFilter', 'StatusFilter', 'AssessmentStatusFilter',
    # 工具函数
    'get_user_info', 'format_user_info_html', 'format_status_badge',
    'format_progress_bar', 'format_duration', 'format_phone_privacy',
    'get_risk_color', 'format_risk_assessment'
]