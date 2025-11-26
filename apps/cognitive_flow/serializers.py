from ninja import Schema
from typing import Dict, Optional

class CognitiveAssessmentSubmitSchema(Schema):
    """认知测评提交参数（上传参数不变）"""
    score_scd: Optional[float] = None
    score_mmse: Optional[float] = None
    score_moca: Optional[float] = None
    score_gad7: Optional[float] = None
    score_phq9: Optional[float] = None
    score_adl: Optional[float] = None
    analysis: Optional[Dict[str, dict]] = None
    started_at: str
    completed_at: str

class CognitiveAssessmentResultSchema(Schema):
    """认知测评结果响应结构"""
    id: int
    user_id: str
    score_scd: Optional[float] = None
    score_mmse: Optional[float] = None
    score_moca: Optional[float] = None
    score_gad7: Optional[float] = None
    score_phq9: Optional[float] = None
    score_adl: Optional[float] = None
    analysis: Dict
    started_at: str
    completed_at: str
    created_at: str
    updated_at: str

class SimpleAssessmentHistorySchema(Schema):
    """认知测评历史记录（极简）"""
    id: int
    score_scd: Optional[float] = None
    score_mmse: Optional[float] = None
    score_moca: Optional[float] = None
    started_at: str
    completed_at: str
    created_at: str