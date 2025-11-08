"""
量表API视图 - 极简设计，后端主导
"""
from ninja import Router, Query
from typing import List, Optional, Dict, Any
from apps.scales.assessment_core import SmartAssessmentService, SingleScaleService
from apps.scales.models import ScaleConfig
from apps.scales.serializers import (
    ScaleConfigResponseSchema, ScaleResultCreateSchema, ScaleResultResponseSchema,
    SmartAssessmentStartResponseSchema,
    SmartAssessmentAnswerSchema, SmartAssessmentAnswerResponseSchema,
    SmartAssessmentResultSchema
)
from config.jwt_auth_adapter import jwt_auth
import logging

logger = logging.getLogger(__name__)

scales_router = Router()

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
        result = SingleScaleService.create_single_scale_result(
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
    """获取单量表结果详情"""
    try:
        result = SingleScaleService.get_single_scale_result(result_id)
        if result:
            return result
        else:
            return {"error": "结果不存在"}
    except Exception as e:
        return {"error": f"获取结果失败: {str(e)}"}

# ========== 智能测评流程接口 ==========

@scales_router.post("/smart-assessment/start", auth=jwt_auth, response=SmartAssessmentStartResponseSchema)
def start_smart_assessment(request):
    """开始智能测评 - 后端通过JWT识别用户"""
    try:
        # 从JWT获取用户ID，而不是从请求数据
        user_id = str(request.user.id)
        assessment = SmartAssessmentService.start_assessment(user_id)
        return {
            'success': True,
            'assessment_id': assessment['id'],
            'next_scale': assessment['next_scale'],
            'total_scales': assessment['total_scales'],
            'message': '智能测评已开始'
        }
        
    except Exception as e:
        logger.error(f"开始智能测评失败: {str(e)}")
        return {"error": f"开始失败: {str(e)}"}

@scales_router.get("/smart-assessment/{assessment_id}", response=SmartAssessmentResultSchema)
def get_smart_assessment_result(request, assessment_id: int):
    """获取智能测评结果 - 精简接口"""
    try:
        result = SmartAssessmentService.get_assessment_result(assessment_id)
        if result:
            # 构建响应数据
            filtered_result = {
                'id': result['id'],
                'user_id': result['user_id'],
                'status': result['status'],
                'scale_responses': result['scale_responses'],
                'scale_scores': result['scale_scores'],
                'results': result['results'],
                'final_result': result['final_result'],
                'total_duration': result['total_duration']
            }
            return filtered_result
        else:
            return {"error": "测评不存在或未完成"}
    except Exception as e:
        logger.error(f"获取智能测评结果失败: {str(e)}")
        return {"error": f"获取失败: {str(e)}"}

@scales_router.post("/smart-assessment/{assessment_id}/answer/{scale_config_id}", auth=jwt_auth, response=SmartAssessmentAnswerResponseSchema)
def submit_smart_answer(request, assessment_id: int, scale_config_id: int, data: SmartAssessmentAnswerSchema):
    """提交智能测评答案"""
    try:
        # 从JWT获取用户ID，验证测评归属
        user_id = str(request.user.id)
        result = SmartAssessmentService.submit_answer(
            assessment_id=assessment_id,
            scale_config_id=scale_config_id,
            user_id=user_id,  # 添加用户ID验证
            selected_options=data.selected_options,
            duration_ms=data.duration_ms,
            started_at=data.started_at,
            completed_at=data.completed_at
        )
        
        if result['success']:
            return {
                'success': True,
                'completed': result['completed'],
                'next_scale': result.get('next_scale'),
                'final_result': result.get('final_result'),
                'message': result['message']
            }
        else:
            return {"error": result.get('error', '提交失败')}
            
    except Exception as e:
        logger.error(f"提交智能测评答案失败: {str(e)}")
        return {"error": f"提交失败: {str(e)}"}
