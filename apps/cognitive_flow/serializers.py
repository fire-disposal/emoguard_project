from ninja import Schema
from typing import Dict, Optional

class CognitiveAssessmentSubmitSchema(Schema):
    # 仅提交测评数据，用户信息由后端自动补全
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
    id: int
    user_id: str
    real_name: Optional[str] = ""
    gender: Optional[str] = ""
    age: Optional[int] = None
    education: Optional[str] = ""
    province: Optional[str] = ""
    city: Optional[str] = ""
    district: Optional[str] = ""
    phone: Optional[str] = ""
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