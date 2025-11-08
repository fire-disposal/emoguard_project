"""
量表管理后台 - 模块化设计，主入口文件
"""
# 从 admin 包导入所有管理类
from apps.scales.admin import (
    ScaleConfigAdmin,
    ScaleResultAdmin,
    SmartAssessmentRecordAdmin
)

# 确保这些类在模块级别可用，便于 Django 发现
__all__ = ['ScaleConfigAdmin', 'ScaleResultAdmin', 'SmartAssessmentRecordAdmin']