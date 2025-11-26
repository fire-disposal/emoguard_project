"""
量表API视图 - 改进版本，更好的代码组织和可维护性
"""

from ninja import Router
from typing import List, Dict, Any
from apps.scales.definitions.registry import ScaleRegistry
from apps.scales.serializers import (
    ScaleResultCreateSchema,
    ScaleResultResponseSchema,
    ScaleResultHistorySchema,
)
from config.jwt_auth_adapter import jwt_auth
import logging

logger = logging.getLogger(__name__)

scales_router = Router(tags=["scales"])


class ScaleResultViewHelper:
    """量表结果视图辅助类 - 处理数据转换和格式化"""

@scales_router.get(
    "/results/history", auth=jwt_auth, response=List[ScaleResultHistorySchema]
)
def get_user_scale_history(request):
    """获取用户量表结果历史（自动适配插件处理类）"""
    try:
        user_id = str(request.user.id)
        from apps.scales.models import ScaleResult

        ScaleRegistry.discover_scales()
        results = ScaleResult.objects.filter(user_id=user_id).order_by("-created_at")
        history_list = []
        for r in results:
            scale_obj = ScaleRegistry.get_scale(r.scale_code)
            analysis = scale_obj.calculate(r.selected_options) if scale_obj else {}
            history_list.append(
                {
                    "id": int(r.id) if r.id is not None else 0,
                    "score": r.score,
                    "scale_type": getattr(scale_obj, "type", "") if scale_obj else "",
                    "conclusion": r.conclusion or analysis.get("interpretation", ""),
                    "created_at": r.created_at.isoformat() if r.created_at else "",
                }
            )
        return history_list
    except Exception as e:
        logger.error(f"量表历史接口异常: {e}", exc_info=True)
        return []


@scales_router.post("/results", auth=jwt_auth, response=Dict[str, Any])
def create_scale_result(request, data: ScaleResultCreateSchema):
    """提交量表结果（无 config 区分）"""
    try:
        user_id = str(request.user.id)
        from apps.scales.definitions.registry import ScaleRegistry

        ScaleRegistry.discover_scales()
        scale_obj = ScaleRegistry.get_scale(data.scale_code)
        if not scale_obj:
            logger.error(f"量表未注册: scale_code={data.scale_code}, data={data}")
            return {
                "error": "量表未注册",
                "debug": {"scale_code": data.scale_code, "data": str(data)},
            }
        analysis = scale_obj.calculate(data.selected_options)
        from apps.scales.models import ScaleResult

        # 优化插件机制：统一通过 ScaleRegistry.calculate 调用，避免实例化参数错误
        from apps.scales.definitions.registry import ScaleRegistry
        analysis = ScaleRegistry.calculate(data.scale_code, data.selected_options)
        result = ScaleResult.objects.create(
            user_id=user_id,
            scale_code=data.scale_code,
            score=analysis.get("score", 0.0),
            selected_options=data.selected_options,
            conclusion=analysis.get("interpretation", ""),
            started_at=data.started_at,
            completed_at=data.completed_at,
        )
        if result:
            logger.info(
                f"量表结果创建成功: id={result.id}, user_id={user_id}, scale_code={data.scale_code}"
            )
            return {
                "id": result.id,
                "score": result.score,
                "success": True,
                "message": "量表结果提交成功",
                "debug": {
                    "user_id": user_id,
                    "scale_code": data.scale_code,
                    "data": str(data),
                },
            }
        else:
            logger.error(
                f"量表结果创建失败: user_id={user_id}, scale_code={data.scale_code}, data={data}"
            )
            return {
                "error": "提交失败",
                "debug": {
                    "user_id": user_id,
                    "scale_code": data.scale_code,
                    "data": str(data),
                },
            }
    except Exception as e:
        logger.error(f"提交量表结果失败: {str(e)}, data={data}")
        return {"error": f"提交失败: {str(e)}", "debug": {"data": str(data)}}


@scales_router.get("/list", response=List[Dict])
def list_scale_types(request):
    """获取所有可用量表类型及元信息（插件机制）"""
    try:
        ScaleRegistry.discover_scales()
        types = []
        for scale_cls in ScaleRegistry.all_scales():
            types.append(scale_cls().get_meta())
        return types
    except Exception as e:
        logger.error(f"获取量表类型失败: {str(e)}")
        return []


@scales_router.get("/{scale_code}/questions", response=List[Dict])
def get_scale_questions(request, scale_code: str):
    """获取指定量表的题目结构（插件机制）"""
    try:
        ScaleRegistry.discover_scales()
        questions = ScaleRegistry.get_questions(scale_code)
        return questions
    except Exception as e:
        logger.error(f"获取量表题目失败: {str(e)}")
        return []


@scales_router.get("/{scale_code}", response=Dict)
def get_scale(request, scale_code: str):
    """获取量表定义详情（无数据库依赖），业务优化：questions结构标准化，前端易用"""
    try:
        ScaleRegistry.discover_scales()
        scale_cls = ScaleRegistry.get_scale(scale_code)
        if not scale_cls:
            return {"error": "量表不存在"}
        # 标准化题目结构，便于前端渲染
        questions = []
        for q in getattr(scale_cls, "questions", []):
            questions.append(
                {
                    "id": q.get("id", ""),
                    "text": q.get("text", ""),
                    "options": q.get("options", []),
                    "type": q.get("type", "single"),
                    "required": q.get("required", True),
                    "order": q.get("order", 0),
                }
            )
        return {
            "code": getattr(scale_cls, "code", ""),
            "name": getattr(scale_cls, "name", ""),
            "version": getattr(scale_cls, "version", ""),
            "description": getattr(scale_cls, "description", ""),
            "type": getattr(scale_cls, "type", ""),
            "questions": questions,
            "status": getattr(scale_cls, "status", ""),
        }
    except Exception as e:
        return {"error": f"获取量表定义失败: {str(e)}"}


@scales_router.get("/results/{result_id}", response=ScaleResultResponseSchema)
def get_scale_result(request, result_id: int):
    """获取单量表结果详情（自动适配插件处理类）"""
    try:
        from apps.scales.models import ScaleResult

        result = ScaleResult.objects.filter(id=result_id).first()
        if not result:
            return {"error": "结果不存在"}
        ScaleRegistry.discover_scales()
        scale_obj = ScaleRegistry.get_scale(result.scale_code)
        questions = getattr(scale_obj, "questions", []) if scale_obj else []
        analysis = scale_obj.calculate(result.selected_options) if scale_obj else {}
        return ScaleResultResponseSchema(
            id=result.id,
            scale_code=result.scale_code,
            questions=questions,
            selected_options=[int(x) for x in result.selected_options],
            score=result.score,
            risk_level=analysis.get("level", ""),
            conclusion=result.conclusion or analysis.get("interpretation", ""),
            duration_ms=int(
                (result.completed_at - result.started_at).total_seconds() * 1000
            )
            if result.started_at and result.completed_at
            else 0,
            started_at=str(result.started_at),
            completed_at=str(result.completed_at),
            status="completed",
            analysis=analysis,
            created_at=str(result.created_at),
        )
    except Exception as e:
        logger.error(f"获取量表结果失败: {str(e)}")
        return {"error": f"获取结果失败: {str(e)}"}


