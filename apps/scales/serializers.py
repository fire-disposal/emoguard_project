from ninja import Schema
from typing import Optional, List


class ScaleResultCreateSchema(Schema):
    """量表结果创建参数"""
    scale_code: str
    selected_options: List[int]
    started_at: str
    completed_at: str

class ScaleResultResponseSchema(Schema):
    """量表结果响应结构"""
    id: int
    scale_code: str
    selected_options: List[int]
    score: float
    conclusion: Optional[str]
    duration_ms: int
    started_at: str
    completed_at: str
    created_at: Optional[str]

class ScaleResultHistorySchema(Schema):
    """量表结果历史记录响应结构"""
    id: int
    score: float
    scale_type: str
    conclusion: str
    created_at: str