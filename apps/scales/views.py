from ninja import Router, Query
from django.shortcuts import get_object_or_404
from datetime import datetime
from typing import Optional
from .models import ScaleConfig, ScaleResult
from .serializers import (
    ScaleConfigCreateSchema, ScaleConfigUpdateSchema, ScaleConfigResponseSchema,
    ScaleResultCreateSchema, ScaleResultResponseSchema, ScaleResultListQuerySchema,
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

from .score_calculator import calculate_score_by_instance

@scales_router.post("/results", response=ScaleResultResponseSchema, auth=jwt_auth)
def create_result(request, data: ScaleResultCreateSchema):
    """
    创建量表结果，自动计算分值与分析
    """
    scale_config = get_object_or_404(ScaleConfig, id=data.scale_config_id)
    selected_options = data.selected_options if isinstance(data.selected_options, list) else []
    started_at = datetime.fromisoformat(data.started_at)
    completed_at = datetime.fromisoformat(data.completed_at)
    # 自动计算答题时长
    try:
        duration_ms = int((completed_at - started_at).total_seconds() * 1000)
    except Exception:
        duration_ms = data.duration_ms
    # 分值与分析
    score_info = calculate_score_by_instance(scale_config, ScaleResult(
        user_id=data.user_id,
        scale_config=scale_config,
        selected_options=selected_options,
        duration_ms=duration_ms,
        started_at=started_at,
        completed_at=completed_at,
    ))
    # 结论字段可存储分析摘要
    result = ScaleResult.objects.create(
        user_id=data.user_id,
        scale_config=scale_config,
        selected_options=selected_options,
        conclusion=f"分值:{score_info['score']} 分级:{score_info['level']} 建议:{'、'.join(score_info['recommendations'])}",
        duration_ms=duration_ms,
        started_at=started_at,
        completed_at=completed_at,
        status='completed',
        analysis=score_info  # 分析结果存储为 JSON 字段
    )
    # 响应中直接返回分析结果
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
        analysis=result.analysis,
        created_at=result.created_at.isoformat(),
        updated_at=result.updated_at.isoformat()
    )
