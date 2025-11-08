from ninja import Schema
from typing import Optional, List, Dict

class HealthReportCreateSchema(Schema):
    assessment_id: int
    report_type: str
    overall_risk: str
    summary: str
    recommendations: List[str]
    professional_advice: str
    trend_analysis: str
    trend_data: Dict
    # 移除user_id字段，从JWT获取或系统自动分配

class HealthReportUpdateSchema(Schema):
    overall_risk: Optional[str] = None
    summary: Optional[str] = None
    recommendations: Optional[List[str]] = None
    professional_advice: Optional[str] = None
    trend_analysis: Optional[str] = None
    trend_data: Optional[Dict] = None

class HealthReportResponseSchema(Schema):
    id: int
    user_id: str
    assessment_id: int
    report_type: str
    overall_risk: str
    summary: str
    recommendations: List[str]
    professional_advice: str
    trend_analysis: str
    trend_data: Dict
    created_at: str
    updated_at: str

class HealthReportListQuerySchema(Schema):
    report_type: Optional[str] = None
    overall_risk: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    page: int = 1
    page_size: int = 10
    # 移除user_id字段，从JWT获取

class HealthReportSummarySchema(Schema):
    total_reports: int
    risk_distribution: Dict[str, int]
    recent_reports: List[HealthReportResponseSchema]
    average_risk_score: float

class HealthTrendSchema(Schema):
    date: str
    risk_level: str
    score: float
    factors: List[str]