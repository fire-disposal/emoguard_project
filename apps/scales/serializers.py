from ninja import Schema
from typing import Optional, List, Dict

class QuestionSchema(Schema):
    id: int
    question: str
    options: List[Dict[str, str]]
    category: Optional[str] = None
    weight: float = 1.0

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
    conclusion: Optional[str] = None
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
    created_at: str
    updated_at: str

class ScaleResultListQuerySchema(Schema):
    user_id: Optional[str] = None
    scale_config_id: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    page: int = 1
    page_size: int = 10

class ScaleAnalysisSchema(Schema):
    total_score: float
    risk_level: str
    recommendations: List[str]
    detailed_analysis: Dict[str, float]
    next_assessment_date: str

class ScaleCompletionSchema(Schema):
    scale_config_id: int
    completion_rate: float
    average_duration: int
    total_completions: int