from ninja import Router
from django.shortcuts import get_object_or_404
from django.utils import timezone
from apps.scales.models import ScaleConfig, ScaleResult, AssessmentResultGroup
from apps.scales.serializers import (
    ScaleResultCreateSchema, ScaleResultResponseSchema, ScaleConfigResponseSchema,
    AssessmentResultGroupResponseSchema, AssessmentResultGroupCreateSchema, GroupedResultSubmitSchema
)
from apps.scales.score_calculator import calculate_score_by_instance
from apps.scales.assessment_flow_engine import CognitiveAssessmentFlowEngine
from config.jwt_auth_adapter import jwt_auth
from datetime import datetime
from apps.users.models import User

scales_router = Router()
@scales_router.post("/results", response=ScaleResultResponseSchema, auth=jwt_auth)
def create_result(request, data: ScaleResultCreateSchema):
    """
    创建量表结果(兼容旧API),自动计算分值与分析
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
    
    # 获取用户资料(用于教育程度校正)
    user_profile = None
    try:
        user = User.objects.get(id=data.user_id)
        user_profile = {
            'education': user.education,
            'age': user.age,
            'gender': user.gender,
        }
    except User.DoesNotExist:
        pass
    
    # 分值与分析
    score_info = calculate_score_by_instance(
        scale_config, 
        ScaleResult(
            user_id=data.user_id,
            scale_config=scale_config,
            selected_options=selected_options,
            duration_ms=duration_ms,
            started_at=started_at,
            completed_at=completed_at,
        ),
        user_profile=user_profile
    )
    
    # 结论字段可存储分析摘要
    result = ScaleResult.objects.create(
        user_id=data.user_id,
        scale_config=scale_config,
        selected_options=selected_options,
        conclusion=f"分值:{score_info['score']} 分级:{score_info['level']}",
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


# ========== 评估流程 API ==========

@scales_router.post("/assessment-groups", response=AssessmentResultGroupResponseSchema, auth=jwt_auth)
def create_assessment_group(request, data: AssessmentResultGroupCreateSchema):
    """
    创建评估结果分组(开始一次评估流程)
    """
    group = AssessmentResultGroup.objects.create(
        user_id=data.user_id,
        flow_type=data.flow_type,
        status='in_progress'
    )
    
    return AssessmentResultGroupResponseSchema(
        id=group.id,
        user_id=str(group.user_id),
        flow_type=group.flow_type,
        status=group.status,
        current_step=group.current_step,
        comprehensive_analysis=group.comprehensive_analysis,
        final_conclusion=group.final_conclusion,
        started_at=group.started_at.isoformat(),
        completed_at=group.completed_at.isoformat() if group.completed_at else None,
        created_at=group.created_at.isoformat(),
        updated_at=group.updated_at.isoformat()
    )


@scales_router.get("/assessment-groups/{group_id}", response=AssessmentResultGroupResponseSchema)
def get_assessment_group(request, group_id: int):
    """
    获取评估分组详情
    """
    group = get_object_or_404(AssessmentResultGroup, id=group_id)
    
    return AssessmentResultGroupResponseSchema(
        id=group.id,
        user_id=str(group.user_id),
        flow_type=group.flow_type,
        status=group.status,
        current_step=group.current_step,
        comprehensive_analysis=group.comprehensive_analysis,
        final_conclusion=group.final_conclusion,
        started_at=group.started_at.isoformat(),
        completed_at=group.completed_at.isoformat() if group.completed_at else None,
        created_at=group.created_at.isoformat(),
        updated_at=group.updated_at.isoformat()
    )


@scales_router.get("/assessment-groups/{group_id}/next-step")
def get_next_step(request, group_id: int):
    """
    获取下一步需要完成的量表
    """
    group = get_object_or_404(AssessmentResultGroup, id=group_id)
    engine = CognitiveAssessmentFlowEngine(group)
    
    return engine.get_next_step()


@scales_router.post("/assessment-groups/{group_id}/submit", response=ScaleResultResponseSchema, auth=jwt_auth)
def submit_grouped_result(request, group_id: int, data: GroupedResultSubmitSchema):
    """
    提交分组量表结果(流程化提交)
    """
    group = get_object_or_404(AssessmentResultGroup, id=group_id)
    scale_config = get_object_or_404(ScaleConfig, id=data.scale_config_id)
    
    selected_options = data.selected_options if isinstance(data.selected_options, list) else []
    started_at = datetime.fromisoformat(data.started_at)
    completed_at = datetime.fromisoformat(data.completed_at)
    
    # 获取用户资料
    user_profile = None
    try:
        user = User.objects.get(id=group.user_id)
        user_profile = {
            'education': user.education,
            'age': user.age,
            'gender': user.gender,
        }
    except User.DoesNotExist:
        pass
    
    # 计算分数
    score_info = calculate_score_by_instance(
        scale_config,
        ScaleResult(
            user_id=group.user_id,
            scale_config=scale_config,
            selected_options=selected_options,
            duration_ms=data.duration_ms,
            started_at=started_at,
            completed_at=completed_at,
        ),
        user_profile=user_profile
    )
    
    # 创建结果并关联到分组
    result = ScaleResult.objects.create(
        user_id=group.user_id,
        scale_config=scale_config,
        result_group=group,  # 关联到分组
        selected_options=selected_options,
        conclusion=f"分值:{score_info['score']} 分级:{score_info['level']}",
        duration_ms=data.duration_ms,
        started_at=started_at,
        completed_at=completed_at,
        status='completed',
        analysis=score_info
    )
    
    # 检查流程是否完成
    engine = CognitiveAssessmentFlowEngine(group)
    next_step = engine.get_next_step()
    
    if next_step['completed']:
        # 生成综合分析
        comprehensive = engine.generate_comprehensive_analysis(user_profile)
        group.comprehensive_analysis = comprehensive
        group.final_conclusion = comprehensive.get('conclusion', '')
        group.status = 'completed'
        group.completed_at = timezone.now()
        
        # 更新用户认知评估完成状态
        try:
            user = User.objects.get(id=group.user_id)
            if not user.has_completed_cognitive_assessment:
                user.has_completed_cognitive_assessment = True
                user.save(update_fields=['has_completed_cognitive_assessment'])
        except User.DoesNotExist:
            pass
    else:
        group.current_step = next_step.get('step', '')
    
    group.save()
    
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
