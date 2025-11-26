from typing import List
from ninja import Router
from apps.cognitive_flow.models import CognitiveAssessmentRecord
from apps.cognitive_flow.serializers import (
    CognitiveAssessmentSubmitSchema,
    CognitiveAssessmentResultSchema,
    SimpleAssessmentHistorySchema,
)
import logging
from config.jwt_auth_adapter import jwt_auth

cognitive_router = Router(tags=["cognitive_flow"])


@cognitive_router.post(
    "/submit", response=CognitiveAssessmentResultSchema, auth=jwt_auth
)
def submit_assessment(request, data: CognitiveAssessmentSubmitSchema):
    logger = logging.getLogger("cognitive_flow.submit")
    try:
        from django.utils.dateparse import parse_datetime

        # 兼容ISO字符串与datetime对象
        def parse_iso(dt):
            if isinstance(dt, str):
                val = parse_datetime(dt)
                if val is None:
                    from datetime import datetime

                    try:
                        val = datetime.fromisoformat(dt)
                    except Exception:
                        val = None
                return val
            return dt

        # 日志打印原始请求数据
        logger.info(f"提交数据: {data.dict() if hasattr(data, 'dict') else data}")

        # 使用JWT认证获取当前用户
        current_user = request.auth

        # 兼容部分字段缺失
        record = CognitiveAssessmentRecord.objects.create(
            user_id=current_user.id,
            score_scd=getattr(data, "score_scd", None),
            score_mmse=getattr(data, "score_mmse", None),
            score_moca=getattr(data, "score_moca", None),
            score_gad7=getattr(data, "score_gad7", None),
            score_phq9=getattr(data, "score_phq9", None),
            score_adl=getattr(data, "score_adl", None),
            analysis=getattr(data, "analysis", {}) or {},
            started_at=parse_iso(getattr(data, "started_at", None)),
            completed_at=parse_iso(getattr(data, "completed_at", None)),
        )
        # 更新用户认知评估完成状态
        try:
            from apps.users.models import User

            User.objects.filter(id=current_user.id).update(
                has_completed_cognitive_assessment=True
            )
        except Exception as update_exc:
            logger.error(f"更新用户认知评估完成状态失败: {update_exc}", exc_info=True)
        logger.info(f"创建测评记录成功: id={record.id}")
        return CognitiveAssessmentResultSchema(
            id=record.id,
            user_id=str(record.user_id),
            score_scd=record.score_scd,
            score_mmse=record.score_mmse,
            score_moca=record.score_moca,
            score_gad7=record.score_gad7,
            score_phq9=record.score_phq9,
            score_adl=record.score_adl,
            analysis=dict(record.analysis) if record.analysis else {},
            started_at=record.started_at.isoformat() if record.started_at else "",
            completed_at=record.completed_at.isoformat() if record.completed_at else "",
            created_at=record.created_at.isoformat() if record.created_at else "",
            updated_at=record.updated_at.isoformat() if record.updated_at else "",
        )
    except Exception as e:
        logger.error(f"认知测评提交异常: {e}", exc_info=True)
        raise


@cognitive_router.get(
    "/history", response=List[SimpleAssessmentHistorySchema], auth=jwt_auth
)
def get_assessment_history(request):
    """
    获取当前用户的认知测评历史记录（极简，仅展示必要字段，按创建时间倒序）
    """
    try:
        from apps.cognitive_flow.models import CognitiveAssessmentRecord
        user_id = request.auth.id
        records = CognitiveAssessmentRecord.objects.filter(user_id=user_id).order_by("-created_at")
        result = []
        for record in records:
            result.append(
                SimpleAssessmentHistorySchema(
                    id=record.id,
                    score_scd=record.score_scd,
                    score_mmse=record.score_mmse,
                    score_moca=record.score_moca,
                    started_at=record.started_at.isoformat() if record.started_at else "",
                    completed_at=record.completed_at.isoformat() if record.completed_at else "",
                    created_at=record.created_at.isoformat() if record.created_at else "",
                )
            )
        return result
    except Exception as e:
        import logging
        logger = logging.getLogger("cognitive_flow.history")
        logger.error(f"认知测评历史接口异常: {e}", exc_info=True)
        return []


@cognitive_router.get(
    "/result/{record_id}", response=CognitiveAssessmentResultSchema, auth=jwt_auth
)
def get_assessment_result(request, record_id: int):
    try:
        current_user = request.auth
        record = CognitiveAssessmentRecord.objects.get(
            id=record_id, user_id=current_user.id
        )
        return CognitiveAssessmentResultSchema(
            id=record.id,
            user_id=str(record.user_id),
            score_scd=record.score_scd,
            score_mmse=record.score_mmse,
            score_moca=record.score_moca,
            score_gad7=record.score_gad7,
            score_phq9=record.score_phq9,
            score_adl=record.score_adl,
            analysis=dict(record.analysis) if record.analysis else {},
            started_at=record.started_at.isoformat() if record.started_at else "",
            completed_at=record.completed_at.isoformat() if record.completed_at else "",
            created_at=record.created_at.isoformat() if record.created_at else "",
            updated_at=record.updated_at.isoformat() if record.updated_at else "",
        )
    except CognitiveAssessmentRecord.DoesNotExist:
        logger = logging.getLogger("cognitive_flow.result")
        logger.error(
            f"记录不存在或无权访问: record_id={record_id}, user_id={current_user.id}"
        )
        raise
    except Exception as e:
        logger = logging.getLogger("cognitive_flow.result")
        logger.error(f"获取认知测评结果异常: {e}", exc_info=True)
        raise
