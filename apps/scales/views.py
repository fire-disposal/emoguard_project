"""
量表API视图 - 改进版本，更好的代码组织和可维护性
"""
from ninja import Router, Query
from typing import List, Optional, Dict, Any
from apps.scales.assessment_core import ScaleResultService
from apps.scales.models import ScaleConfig
from apps.scales.serializers import (
    ScaleConfigResponseSchema, ScaleResultCreateSchema, ScaleResultResponseSchema,
)
from config.jwt_auth_adapter import jwt_auth
import logging

logger = logging.getLogger(__name__)

scales_router = Router(tags=["scales"])


class ScaleResultViewHelper:
    """量表结果视图辅助类 - 处理数据转换和格式化"""


    @staticmethod
    def format_scale_config_data(scale_config) -> Optional[Dict[str, Any]]:
        """格式化量表配置数据"""
        if not scale_config:
            return None
            
        return {
            'id': getattr(scale_config, 'id', 0) or 0,
            'name': getattr(scale_config, 'name', '') or '',
            'code': getattr(scale_config, 'code', '') or '',
            'version': getattr(scale_config, 'version', '') or '',
            'description': getattr(scale_config, 'description', '') or '',
            'type': getattr(scale_config, 'type', '') or '',
            'questions': getattr(scale_config, 'questions', []) or [],
            'status': getattr(scale_config, 'status', '') or '',
        }
    
    @staticmethod
    def format_scale_result_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化量表结果数据"""
        if not raw_data:
            return {}
            
        scale_config = raw_data.get('scale_config')
        
        return {
            'id': raw_data.get('id', 0) or 0,
            'scale_config': ScaleResultViewHelper.format_scale_config_data(scale_config),
            'selected_options': raw_data.get('selected_options', []) or [],
            'conclusion': raw_data.get('conclusion', '') or '',
            'duration_ms': raw_data.get('duration_ms', 0) or 0,
            'started_at': raw_data.get('started_at', '') or '',
            'completed_at': raw_data.get('completed_at', '') or '',
            'status': raw_data.get('status', '') or '',
            'analysis': raw_data.get('analysis', {}) or {},
        }


# ========== 单量表功能接口 ==========

@scales_router.get("/configs", response=List[ScaleConfigResponseSchema])
def list_configs(request, status: Optional[str] = Query(None)):
    """获取量表配置列表 - 精简接口"""
    try:
        queryset = ScaleConfig.objects.all()
        if status:
            queryset = queryset.filter(status=status)
        
        configs = list(queryset.order_by('-created_at'))
        
        # 确保数据格式正确并构建精简响应
        result = []
        for config in configs:
            # 确保questions中的value是字符串
            questions = config.questions or []
            for question in questions:
                if 'options' in question:
                    for option in question['options']:
                        if 'value' in option:
                            option['value'] = str(option['value'])
            
            result.append({
                'id': config.id,
                'name': config.name,
                'code': config.code,
                'version': config.version,
                'description': config.description,
                'type': config.type,
                'questions': questions,
                'status': config.status
            })
        
        return result
        
    except Exception as e:
        logger.error(f"获取量表配置失败: {str(e)}")
        return []

@scales_router.get("/configs/{config_id}", response=ScaleConfigResponseSchema)
def get_config(request, config_id: int):
    """获取量表配置详情 - 精简接口"""
    try:
        config = ScaleConfig.objects.get(id=config_id)
        
        # 确保数据格式正确并构建精简响应
        questions = config.questions or []
        for question in questions:
            if 'options' in question:
                for option in question['options']:
                    if 'value' in option:
                        option['value'] = str(option['value'])
        
        return {
            'id': config.id,
            'name': config.name,
            'code': config.code,
            'version': config.version,
            'description': config.description,
            'type': config.type,
            'questions': questions,
            'status': config.status
        }
    except ScaleConfig.DoesNotExist:
        return {"error": "量表配置不存在"}
    except Exception as e:
        return {"error": f"获取量表配置失败: {str(e)}"}

@scales_router.post("/results", auth=jwt_auth, response=Dict[str, Any])
def create_single_result(request, data: ScaleResultCreateSchema):
    """提交单量表结果"""
    try:
        # 从JWT获取用户ID
        user_id = str(request.user.id)
        result = ScaleResultService.create_single_scale_result(
            user_id=user_id,
            scale_config_id=data.scale_config_id,
            selected_options=data.selected_options,
            duration_ms=data.duration_ms,
            started_at=data.started_at,
            completed_at=data.completed_at
        )
        
        if result:
            return {
                'id': result.id,
                'success': True,
                'message': '量表结果提交成功'
            }
        else:
            return {"error": "提交失败"}
            
    except Exception as e:
        logger.error(f"提交单量表结果失败: {str(e)}")
        return {"error": f"提交失败: {str(e)}"}

@scales_router.get("/results/{result_id}", response=ScaleResultResponseSchema)
def get_single_result(request, result_id: int):
    """获取单量表结果详情 - 改进版本"""
    try:
        raw_data = ScaleResultService.get_single_scale_result(result_id)
        if not raw_data:
            return {"error": "结果不存在"}
        
        # 使用辅助类进行数据格式化
        return ScaleResultViewHelper.format_scale_result_data(raw_data)
        
    except Exception as e:
        logger.error(f"获取单量表结果失败: {str(e)}")
        return {"error": f"获取结果失败: {str(e)}"}

@scales_router.get("/results/history", auth=jwt_auth, response=List[ScaleResultResponseSchema])
def get_user_results_history(request):
    """
    获取当前用户的所有量表历史结果（仅返回自己的，按创建时间倒序，字段精简）
    """
    user_id = str(request.user.id)
    # 获取所有结果，不限制数量
    results = ScaleResultService.get_user_scale_results(user_id, limit=1000)
    # 格式化为响应结构
    response = []
    for result in results:
        # 只保留指定字段
        response.append(
            ScaleResultResponseSchema(
                id=result.id,
                scale_config=result.scale_config,
                selected_options=result.selected_options,
                conclusion=result.conclusion,
                duration_ms=result.duration_ms,
                started_at=result.started_at.isoformat() if result.started_at else "",
                completed_at=result.completed_at.isoformat() if result.completed_at else "",
                status=result.status,
                analysis=result.analysis,
                created_at=result.created_at.isoformat() if hasattr(result, "created_at") else "",
            )
        )
    # 按创建时间倒序（数据库已排序，保险起见再排序一次）
    response.sort(key=lambda x: x.created_at, reverse=True)
    return response
    