from ninja import Router, Query
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django.utils import timezone
from datetime import datetime, timedelta
from typing import Optional
from .models import ScaleConfig, ScaleResult
from .serializers import (
    ScaleConfigCreateSchema, ScaleConfigUpdateSchema, ScaleConfigResponseSchema,
    ScaleResultCreateSchema, ScaleResultResponseSchema, ScaleResultListQuerySchema,
    ScaleAnalysisSchema, ScaleCompletionSchema
)
from config.jwt_auth_adapter import jwt_auth

scales_router = Router()

@scales_router.get("/configs", response=list[ScaleConfigResponseSchema])
def list_configs(request, status: Optional[str] = Query(None), type: Optional[str] = Query(None)):
    """
    获取量表配置列表，支持状态和类型过滤
    """
    queryset = ScaleConfig.objects.all()
    
    if status:
        queryset = queryset.filter(status=status)
    if type:
        queryset = queryset.filter(type=type)
    
    configs = queryset.order_by('-created_at')
    
    return [
        ScaleConfigResponseSchema(
            id=c.id,
            name=c.name,
            code=c.code,
            version=c.version,
            description=c.description,
            type=c.type,
            questions=c.questions if isinstance(c.questions, list) else [],
            status=c.status,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat()
        )
        for c in configs
    ]

@scales_router.get("/configs/{config_id}", response=ScaleConfigResponseSchema)
def get_config(request, config_id: int):
    """
    获取单个量表配置详情
    """
    config = get_object_or_404(ScaleConfig, id=config_id)
    return ScaleConfigResponseSchema(
        id=config.id,
        name=config.name,
        code=config.code,
        version=config.version,
        description=config.description,
        type=config.type,
        questions=config.questions if isinstance(config.questions, list) else [],
        status=config.status,
        created_at=config.created_at.isoformat(),
        updated_at=config.updated_at.isoformat()
    )

@scales_router.post("/configs", response=ScaleConfigResponseSchema, auth=jwt_auth)
def create_config(request, data: ScaleConfigCreateSchema):
    """
    创建量表配置
    """
    config = ScaleConfig.objects.create(
        name=data.name,
        code=data.code,
        version=data.version,
        description=data.description,
        type=data.type,
        questions=[q.dict() for q in data.questions],
        status=data.status
    )
    
    return ScaleConfigResponseSchema(
        id=config.id,
        name=config.name,
        code=config.code,
        version=config.version,
        description=config.description,
        type=config.type,
        questions=config.questions if isinstance(config.questions, list) else [],
        status=config.status,
        created_at=config.created_at.isoformat(),
        updated_at=config.updated_at.isoformat()
    )

@scales_router.put("/configs/{config_id}", response=ScaleConfigResponseSchema, auth=jwt_auth)
def update_config(request, config_id: int, data: ScaleConfigUpdateSchema):
    """
    更新量表配置
    """
    config = get_object_or_404(ScaleConfig, id=config_id)
    
    if data.name is not None:
        config.name = data.name
    if data.description is not None:
        config.description = data.description
    if data.questions is not None:
        config.questions = [q.dict() for q in data.questions]
    if data.status is not None:
        config.status = data.status
    
    config.save()
    
    return ScaleConfigResponseSchema(
        id=config.id,
        name=config.name,
        code=config.code,
        version=config.version,
        description=config.description,
        type=config.type,
        questions=config.questions if isinstance(config.questions, list) else [],
        status=config.status,
        created_at=config.created_at.isoformat(),
        updated_at=config.updated_at.isoformat()
    )

@scales_router.get("/results", response=list[ScaleResultResponseSchema])
def list_results(request, filters: ScaleResultListQuerySchema = Query(...)):
    """
    获取量表结果列表，支持多种过滤条件和分页
    """
    queryset = ScaleResult.objects.select_related('scale_config')
    
    if filters.user_id:
        queryset = queryset.filter(user_id=filters.user_id)
    if filters.scale_config_id:
        queryset = queryset.filter(scale_config_id=filters.scale_config_id)
    if filters.start_date:
        start_datetime = datetime.fromisoformat(filters.start_date)
        queryset = queryset.filter(created_at__gte=start_datetime)
    if filters.end_date:
        end_datetime = datetime.fromisoformat(filters.end_date)
        queryset = queryset.filter(created_at__lte=end_datetime)
    
    # 分页
    start = (filters.page - 1) * filters.page_size
    end = start + filters.page_size
    results = queryset[start:end]
    
    return [
        ScaleResultResponseSchema(
            id=r.id,
            user_id=str(r.user_id),
            scale_config=ScaleConfigResponseSchema(
                id=r.scale_config.id,
                name=r.scale_config.name,
                code=r.scale_config.code,
                version=r.scale_config.version,
                description=r.scale_config.description,
                type=r.scale_config.type,
                questions=r.scale_config.questions if isinstance(r.scale_config.questions, list) else [],
                status=r.scale_config.status,
                created_at=r.scale_config.created_at.isoformat(),
                updated_at=r.scale_config.updated_at.isoformat()
            ),
            selected_options=r.selected_options if isinstance(r.selected_options, list) else [],
            conclusion=r.conclusion,
            duration_ms=r.duration_ms,
            started_at=r.started_at.isoformat(),
            completed_at=r.completed_at.isoformat(),
            status=r.status,
            created_at=r.created_at.isoformat(),
            updated_at=r.updated_at.isoformat()
        )
        for r in results
    ]

@scales_router.get("/results/{result_id}", response=ScaleResultResponseSchema)
def get_result(request, result_id: int):
    """
    获取单个量表结果详情
    """
    result = get_object_or_404(ScaleResult, id=result_id)
    return ScaleResultResponseSchema(
        id=result.id,
        user_id=str(result.user_id),
        scale_config=ScaleConfigResponseSchema(
            id=result.scale_config.id,
            name=result.scale_config.name,
            code=result.scale_config.code,
            version=result.scale_config.version,
            description=result.scale_config.description,
            type=result.scale_config.type,
            questions=result.scale_config.questions if isinstance(result.scale_config.questions, list) else [],
            status=result.scale_config.status,
            created_at=result.scale_config.created_at.isoformat(),
            updated_at=result.scale_config.updated_at.isoformat()
        ),
        selected_options=result.selected_options if isinstance(result.selected_options, list) else [],
        conclusion=result.conclusion,
        duration_ms=result.duration_ms,
        started_at=result.started_at.isoformat(),
        completed_at=result.completed_at.isoformat(),
        status=result.status,
        created_at=result.created_at.isoformat(),
        updated_at=result.updated_at.isoformat()
    )

@scales_router.post("/results", response=ScaleResultResponseSchema, auth=jwt_auth)
def create_result(request, data: ScaleResultCreateSchema):
    """
    创建量表结果
    """
    scale_config = get_object_or_404(ScaleConfig, id=data.scale_config_id)
    
    result = ScaleResult.objects.create(
        user_id=data.user_id,
        scale_config=scale_config,
        selected_options=data.selected_options if isinstance(data.selected_options, list) else [],
        conclusion=data.conclusion,
        duration_ms=data.duration_ms,
        started_at=datetime.fromisoformat(data.started_at),
        completed_at=datetime.fromisoformat(data.completed_at),
        status='completed'
    )
    
    return ScaleResultResponseSchema(
        id=result.id,
        user_id=str(result.user_id),
        scale_config=ScaleConfigResponseSchema(
            id=result.scale_config.id,
            name=result.scale_config.name,
            code=result.scale_config.code,
            version=result.scale_config.version,
            description=result.scale_config.description,
            type=result.scale_config.type,
            questions=result.scale_config.questions if isinstance(result.scale_config.questions, list) else [],
            status=result.scale_config.status,
            created_at=result.scale_config.created_at.isoformat(),
            updated_at=result.scale_config.updated_at.isoformat()
        ),
        selected_options=result.selected_options if isinstance(result.selected_options, list) else [],
        conclusion=result.conclusion,
        duration_ms=result.duration_ms,
        started_at=result.started_at.isoformat(),
        completed_at=result.completed_at.isoformat(),
        status=result.status,
        created_at=result.created_at.isoformat(),
        updated_at=result.updated_at.isoformat()
    )

@scales_router.post("/results/{result_id}/analyze", response=ScaleAnalysisSchema, auth=jwt_auth)
def analyze_result(request, result_id: int):
    """
    分析量表结果
    """
    result = get_object_or_404(ScaleResult, id=result_id)
    
    # 这里实现具体的分析逻辑
    # 根据选择的选项计算总分
    total_score = sum(result.selected_options) if result.selected_options else 0
    
    # 根据分数确定风险等级
    if total_score <= 10:
        risk_level = "低风险"
    elif total_score <= 20:
        risk_level = "中风险"
    elif total_score <= 30:
        risk_level = "高风险"
    else:
        risk_level = "极高风险"
    
    # 生成建议
    recommendations = []
    if risk_level == "高风险":
        recommendations.append("建议寻求专业心理咨询")
        recommendations.append("保持规律的作息时间")
    elif risk_level == "中风险":
        recommendations.append("建议进行放松训练")
        recommendations.append("增加社交活动")
    else:
        recommendations.append("继续保持良好的生活习惯")
        recommendations.append("定期进行自我评估")
    
    # 详细分析
    detailed_analysis = {
        "情绪状态": 0.8,
        "社交功能": 0.6,
        "睡眠质量": 0.7,
        "工作压力": 0.5
    }
    
    # 下次评估日期
    next_assessment = timezone.now() + timedelta(days=30)
    
    return ScaleAnalysisSchema(
        total_score=float(total_score),
        risk_level=risk_level,
        recommendations=recommendations,
        detailed_analysis=detailed_analysis,
        next_assessment_date=next_assessment.date().isoformat()
    )

@scales_router.get("/completion-stats", response=list[ScaleCompletionSchema])
def get_completion_stats(request, days: int = Query(30)):
    """
    获取量表完成统计
    """
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # 获取所有量表配置
    configs = ScaleConfig.objects.all()
    stats = []
    
    for config in configs:
        # 获取该量表的完成数量
        completions = ScaleResult.objects.filter(
            scale_config=config,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        total_completions = completions.count()
        
        # 计算平均完成时间
        avg_duration = completions.aggregate(
            avg_duration=Avg('duration_ms')
        )['avg_duration'] or 0
        
        # 计算完成率（这里简化处理，假设所有注册用户都应该完成）
        completion_rate = 0.75  # 默认值，实际应该基于注册用户计算
        
        stats.append(ScaleCompletionSchema(
            scale_config_id=config.id,
            completion_rate=completion_rate,
            average_duration=int(avg_duration),
            total_completions=total_completions
        ))
    
    return stats