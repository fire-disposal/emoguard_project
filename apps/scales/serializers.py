from ninja import Schema
from typing import Optional, List, Dict, Union
from datetime import datetime

class QuestionOptionSchema(Schema):
    text: str
    value: str  # 确保value是字符串

class QuestionSchema(Schema):
    id: int
    question: str
    options: List[QuestionOptionSchema]

class ScaleConfigResponseSchema(Schema):
    id: int
    name: str
    code: str
    version: str
    description: Optional[str]
    type: str
    questions: List[QuestionSchema]
    status: str

class ScaleResultCreateSchema(Schema):
    scale_config_id: int
    selected_options: List[int]
    duration_ms: int
    started_at: str
    completed_at: str

class ScaleResultResponseSchema(Schema):
    id: int
    user_id: str
    scale_config: ScaleConfigResponseSchema
    selected_options: List[int]
    conclusion: Optional[str]
    duration_ms: int
    started_at: str
    completed_at: str
    status: str
    analysis: Dict
    # 移除created_at和updated_at，前端不需要这些字段

class SmartAssessmentStartSchema(Schema):
    """开始智能测评"""
    # 移除user_id字段，从JWT获取

class SmartAssessmentStartResponseSchema(Schema):
    """智能测评开始响应"""
    success: bool
    assessment_id: int
    next_scale: Optional[Dict]
    total_scales: int
    strategy: str
    message: str

class SmartAssessmentAnswerSchema(Schema):
    """提交智能测评答案"""
    selected_options: List[int]
    duration_ms: int
    started_at: str
    completed_at: str

class SmartAssessmentAnswerResponseSchema(Schema):
    """提交答案响应"""
    success: bool
    completed: bool
    next_scale: Optional[Dict]
    final_result: Optional[Dict]
    message: str

class SmartAssessmentResultSchema(Schema):
    """智能测评结果 - 精简版"""
    id: int
    user_id: str
    status: str
    strategy: str
    results: List[Dict]
    final_result: Dict
    total_duration: int
    # 移除started_at和completed_at，前端不需要这些字段