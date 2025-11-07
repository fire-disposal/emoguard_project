from ninja import Schema
from typing import Optional, List, Dict

class QuestionSchema(Schema):
    id: int
    question: str
    options: List[Dict[str, str]]

class ScaleConfigCreateSchema(Schema):
    name: str
    code: str
    version: str
    description: Optional[str] = None
    type: str
    questions: List[QuestionSchema]
    status: str = "draft"

class ScaleConfigUpdateSchema(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    questions: Optional[List[QuestionSchema]] = None
    status: Optional[str] = None

class ScaleConfigResponseSchema(Schema):
    id: int
    name: str
    code: str
    version: str
    description: Optional[str]
    type: str
    questions: List[QuestionSchema]
    status: str
    created_at: str
    updated_at: str

class ScaleResultCreateSchema(Schema):
    user_id: str
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
    created_at: str
    updated_at: str

class AssessmentResultGroupCreateSchema(Schema):
    """创建评估分组"""
    user_id: str
    flow_type: str = "cognitive_assessment"


class AssessmentResultGroupResponseSchema(Schema):
    """评估分组响应"""
    id: int
    user_id: str
    flow_type: str
    status: str
    current_step: str
    comprehensive_analysis: Dict
    final_conclusion: str
    started_at: str
    completed_at: Optional[str] = None
    created_at: str
    updated_at: str


class GroupedResultSubmitSchema(Schema):
    """分组提交量表结果"""
    result_group_id: int
    scale_config_id: int
    selected_options: List[int]
    duration_ms: int
    started_at: str
    completed_at: str