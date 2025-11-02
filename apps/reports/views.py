from ninja import Router, Query
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import HealthReport
from .serializers import (
    HealthReportCreateSchema, HealthReportUpdateSchema, HealthReportResponseSchema,
    HealthReportListQuerySchema, HealthReportSummarySchema, HealthTrendSchema
)

reports_router = Router()

@reports_router.get("/", response=list[HealthReportResponseSchema])
def list_reports(request, filters: HealthReportListQuerySchema = Query(...)):
    """
    获取健康报告列表，支持多种过滤条件和分页
    """
    queryset = HealthReport.objects.all()
    
    # 用户过滤
    if filters.user_id:
        queryset = queryset.filter(user_id=filters.user_id)
    
    # 报告类型过滤
    if filters.report_type:
        queryset = queryset.filter(report_type=filters.report_type)
    
    # 风险等级过滤
    if filters.overall_risk:
        queryset = queryset.filter(overall_risk=filters.overall_risk)
    
    # 日期范围过滤
    if filters.start_date:
        start_datetime = datetime.fromisoformat(filters.start_date)
        queryset = queryset.filter(created_at__gte=start_datetime)
    
    if filters.end_date:
        end_datetime = datetime.fromisoformat(filters.end_date)
        queryset = queryset.filter(created_at__lte=end_datetime)
    
    # 分页
    start = (filters.page - 1) * filters.page_size
    end = start + filters.page_size
    reports = queryset[start:end]
    
    return [
        HealthReportResponseSchema(
            id=r.id,
            user_id=str(r.user_id),
            assessment_id=r.assessment_id,
            report_type=r.report_type,
            overall_risk=r.overall_risk,
            summary=r.summary,
            recommendations=r.recommendations,
            professional_advice=r.professional_advice,
            trend_analysis=r.trend_analysis,
            trend_data=r.trend_data,
            created_at=r.created_at.isoformat(),
            updated_at=r.updated_at.isoformat()
        )
        for r in reports
    ]

@reports_router.get("/{report_id}", response=HealthReportResponseSchema)
def get_report(request, report_id: int):
    """
    获取单份健康报告详情
    """
    report = get_object_or_404(HealthReport, id=report_id)
    return HealthReportResponseSchema(
        id=report.id,
        user_id=str(report.user_id),
        assessment_id=report.assessment_id,
        report_type=report.report_type,
        overall_risk=report.overall_risk,
        summary=report.summary,
        recommendations=report.recommendations,
        professional_advice=report.professional_advice,
        trend_analysis=report.trend_analysis,
        trend_data=report.trend_data,
        created_at=report.created_at.isoformat(),
        updated_at=report.updated_at.isoformat()
    )

@reports_router.post("/", response=HealthReportResponseSchema)
def create_report(request, data: HealthReportCreateSchema):
    """
    创建健康报告
    """
    report = HealthReport.objects.create(
        user_id=data.user_id,
        assessment_id=data.assessment_id,
        report_type=data.report_type,
        overall_risk=data.overall_risk,
        summary=data.summary,
        recommendations=data.recommendations,
        professional_advice=data.professional_advice,
        trend_analysis=data.trend_analysis,
        trend_data=data.trend_data
    )
    
    return HealthReportResponseSchema(
        id=report.id,
        user_id=str(report.user_id),
        assessment_id=report.assessment_id,
        report_type=report.report_type,
        overall_risk=report.overall_risk,
        summary=report.summary,
        recommendations=report.recommendations,
        professional_advice=report.professional_advice,
        trend_analysis=report.trend_analysis,
        trend_data=report.trend_data,
        created_at=report.created_at.isoformat(),
        updated_at=report.updated_at.isoformat()
    )

@reports_router.put("/{report_id}", response=HealthReportResponseSchema)
def update_report(request, report_id: int, data: HealthReportUpdateSchema):
    """
    更新健康报告
    """
    report = get_object_or_404(HealthReport, id=report_id)
    
    # 更新字段
    if data.overall_risk is not None:
        report.overall_risk = data.overall_risk
    if data.summary is not None:
        report.summary = data.summary
    if data.recommendations is not None:
        report.recommendations = data.recommendations
    if data.professional_advice is not None:
        report.professional_advice = data.professional_advice
    if data.trend_analysis is not None:
        report.trend_analysis = data.trend_analysis
    if data.trend_data is not None:
        report.trend_data = data.trend_data
    
    report.save()
    
    return HealthReportResponseSchema(
        id=report.id,
        user_id=str(report.user_id),
        assessment_id=report.assessment_id,
        report_type=report.report_type,
        overall_risk=report.overall_risk,
        summary=report.summary,
        recommendations=report.recommendations,
        professional_advice=report.professional_advice,
        trend_analysis=report.trend_analysis,
        trend_data=report.trend_data,
        created_at=report.created_at.isoformat(),
        updated_at=report.updated_at.isoformat()
    )

@reports_router.delete("/{report_id}")
def delete_report(request, report_id: int):
    """
    删除健康报告
    """
    report = get_object_or_404(HealthReport, id=report_id)
    report.delete()
    return {"message": "健康报告删除成功"}

@reports_router.get("/summary/{user_id}", response=HealthReportSummarySchema)
def get_user_report_summary(request, user_id: str):
    """
    获取用户的健康报告摘要
    """
    user_reports = HealthReport.objects.filter(user_id=user_id)
    total_reports = user_reports.count()
    
    # 风险等级分布
    risk_distribution = user_reports.values('overall_risk').annotate(
        count=Count('id')
    ).order_by('-count')
    
    risk_dict = {item['overall_risk']: item['count'] for item in risk_distribution}
    
    # 最近的报告
    recent_reports = user_reports.order_by('-created_at')[:5]
    
    # 计算平均风险分数（这里假设风险等级可以转换为分数）
    risk_scores = {
        '低风险': 1,
        '中风险': 2,
        '高风险': 3,
        '极高风险': 4
    }
    
    total_score = 0
    valid_reports = 0
    
    for report in user_reports:
        if report.overall_risk in risk_scores:
            total_score += risk_scores[report.overall_risk]
            valid_reports += 1
    
    average_risk_score = total_score / valid_reports if valid_reports > 0 else 0
    
    return HealthReportSummarySchema(
        total_reports=total_reports,
        risk_distribution=risk_dict,
        recent_reports=[
            HealthReportResponseSchema(
                id=r.id,
                user_id=str(r.user_id),
                assessment_id=r.assessment_id,
                report_type=r.report_type,
                overall_risk=r.overall_risk,
                summary=r.summary,
                recommendations=r.recommendations,
                professional_advice=r.professional_advice,
                trend_analysis=r.trend_analysis,
                trend_data=r.trend_data,
                created_at=r.created_at.isoformat(),
                updated_at=r.updated_at.isoformat()
            )
            for r in recent_reports
        ],
        average_risk_score=round(average_risk_score, 2)
    )

@reports_router.get("/trends/{user_id}", response=list[HealthTrendSchema])
def get_health_trends(request, user_id: str, days: int = Query(90)):
    """
    获取用户健康趋势
    """
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    reports = HealthReport.objects.filter(
        user_id=user_id,
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).order_by('created_at')
    
    trends = []
    for report in reports:
        # 提取趋势数据中的关键因素
        factors = report.trend_data.get('key_factors', []) if isinstance(report.trend_data, dict) else []
        
        # 将风险等级转换为分数
        risk_score = {
            '低风险': 1,
            '中风险': 2,
            '高风险': 3,
            '极高风险': 4
        }.get(report.overall_risk, 2)
        
        trends.append(HealthTrendSchema(
            date=report.created_at.date().isoformat(),
            risk_level=report.overall_risk,
            score=risk_score,
            factors=factors[:3]  # 只取前3个因素
        ))
    
    return trends
