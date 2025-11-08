from ninja import Schema
from typing import Optional, List, Dict

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

class SmartAssessmentStartResponseSchema(Schema):
    """智能测评开始响应"""
    success: bool
    assessment_id: int
    next_scale: Optional[Dict]
    total_scales: int
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
    scale_responses: List[Dict]
    scale_scores: List[Dict]
    results: List[Dict]
    final_result: Dict
    total_duration: int