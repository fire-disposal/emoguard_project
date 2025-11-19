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
    scale_config: ScaleConfigResponseSchema
    selected_options: List[int]
    conclusion: Optional[str]
    duration_ms: int
    started_at: str
    completed_at: str
    status: str
    analysis: Dict