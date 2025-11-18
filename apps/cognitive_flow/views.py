from ninja import Router
from apps.cognitive_flow.models import CognitiveAssessmentRecord
from apps.cognitive_flow.serializers import (
    CognitiveAssessmentSubmitSchema, CognitiveAssessmentResultSchema
)
import logging
from config.jwt_auth_adapter import jwt_auth

cognitive_router = Router()

@cognitive_router.post("/submit", response=CognitiveAssessmentResultSchema, auth=jwt_auth)
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
            real_name=getattr(current_user, "real_name", ""),
            gender=getattr(current_user, "gender", ""),
            age=getattr(current_user, "age", None),
            education=getattr(current_user, "education", ""),
            province=getattr(current_user, "province", ""),
            city=getattr(current_user, "city", ""),
            district=getattr(current_user, "district", ""),
            phone=getattr(current_user, "phone", ""),
            score_scd=getattr(data, "score_scd", None),
            score_mmse=getattr(data, "score_mmse", None),
            score_moca=getattr(data, "score_moca", None),
            score_gad7=getattr(data, "score_gad7", None),
            score_phq9=getattr(data, "score_phq9", None),
            score_adl=getattr(data, "score_adl", None),
            score_sus=getattr(data, "score_sus", None),
            analysis=getattr(data, "analysis", {}) or {},
            started_at=parse_iso(getattr(data, "started_at", None)),
            completed_at=parse_iso(getattr(data, "completed_at", None))
        )
        logger.info(f"创建测评记录成功: id={record.id}")
        return CognitiveAssessmentResultSchema(
            id=record.id,
            user_id=str(record.user_id),
            real_name=record.real_name,
            gender=record.gender,
            age=record.age,
            education=record.education,
            province=record.province,
            city=record.city,
            district=record.district,
            phone=record.phone,
            score_scd=record.score_scd,
            score_mmse=record.score_mmse,
            score_moca=record.score_moca,
            score_gad7=record.score_gad7,
            score_phq9=record.score_phq9,
            score_adl=record.score_adl,
            score_sus=record.score_sus,
            analysis=record.analysis,
            started_at=record.started_at.isoformat() if record.started_at else None,
            completed_at=record.completed_at.isoformat() if record.completed_at else None,
            created_at=record.created_at.isoformat(),
            updated_at=record.updated_at.isoformat()
        )
    except Exception as e:
        logger.error(f"认知测评提交异常: {e}", exc_info=True)
        raise

@cognitive_router.get("/result/{record_id}", response=CognitiveAssessmentResultSchema, auth=jwt_auth)
def get_assessment_result(request, record_id: int):
    try:
        current_user = request.auth
        record = CognitiveAssessmentRecord.objects.get(id=record_id, user_id=current_user.id)
        return CognitiveAssessmentResultSchema(
            id=record.id,
            user_id=str(record.user_id),
            real_name=record.real_name,
            gender=record.gender,
            age=record.age,
            education=record.education,
            province=record.province,
            city=record.city,
            district=record.district,
            phone=record.phone,
            score_scd=record.score_scd,
            score_mmse=record.score_mmse,
            score_moca=record.score_moca,
            score_gad7=record.score_gad7,
            score_phq9=record.score_phq9,
            score_adl=record.score_adl,
            score_sus=record.score_sus,
            analysis=record.analysis,
            started_at=record.started_at.isoformat() if record.started_at else None,
            completed_at=record.completed_at.isoformat() if record.completed_at else None,
            created_at=record.created_at.isoformat(),
            updated_at=record.updated_at.isoformat()
        )
    except CognitiveAssessmentRecord.DoesNotExist:
        logger = logging.getLogger("cognitive_flow.result")
        logger.error(f"记录不存在或无权访问: record_id={record_id}, user_id={current_user.id}")
        raise
    except Exception as e:
        logger = logging.getLogger("cognitive_flow.result")
        logger.error(f"获取认知测评结果异常: {e}", exc_info=True)
        raise