"""
响应服务 - 统一处理响应格式构建
"""
from typing import Dict, Any
from apps.scales.models import ScaleResult, ScaleConfig


class ResponseService:
    """响应服务类 - 统一构建所有响应格式"""
    
    @staticmethod
    def build_scale_result_response(result: ScaleResult) -> Dict[str, Any]:
        """
        构建量表结果响应
        
        Args:
            result: ScaleResult实例
            
        Returns:
            响应数据字典
        """
        return {
            'id': result.id,
            'user_id': str(result.user_id),
            'scale_config': ResponseService.build_scale_config_response(result.scale_config),
            'selected_options': result.selected_options if isinstance(result.selected_options, list) else [],
            'conclusion': result.conclusion or '',
            'duration_ms': result.duration_ms,
            'started_at': result.started_at.isoformat(),
            'completed_at': result.completed_at.isoformat(),
            'status': result.status,
            'analysis': result.analysis or {},
            'created_at': result.created_at.isoformat(),
            'updated_at': result.updated_at.isoformat()
        }
    
    @staticmethod
    def build_scale_config_response(scale_config: ScaleConfig) -> Dict[str, Any]:
        """
        构建量表配置响应
        
        Args:
            scale_config: ScaleConfig实例
            
        Returns:
            量表配置响应数据字典
        """
        return {
            'id': scale_config.id,
            'name': scale_config.name,
            'code': scale_config.code,
            'version': scale_config.version,
            'description': scale_config.description or '',
            'type': scale_config.type,
            'questions': scale_config.questions if isinstance(scale_config.questions, list) else [],
            'status': scale_config.status,
            'created_at': scale_config.created_at.isoformat(),
            'updated_at': scale_config.updated_at.isoformat()
        }
    
    @staticmethod
    def build_next_step_response(next_step_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建下一步步骤响应
        
        Args:
            next_step_info: 下一步步骤信息
            
        Returns:
            下一步步骤响应数据字典
        """
        return {
            'completed': next_step_info.get('completed', False),
            'next_scales': next_step_info.get('next_scales', []),
            'reason': next_step_info.get('reason', ''),
            'step': next_step_info.get('step', '')
        }
    
    @staticmethod
    def build_error_response(error_message: str, error_code: str = 'INTERNAL_ERROR') -> Dict[str, Any]:
        """
        构建错误响应
        
        Args:
            error_message: 错误信息
            error_code: 错误代码
            
        Returns:
            错误响应数据字典
        """
        return {
            'error': True,
            'error_code': error_code,
            'error_message': error_message
        }
    
    @staticmethod
    def build_success_response(data: Any = None, message: str = '操作成功') -> Dict[str, Any]:
        """
        构建成功响应
        
        Args:
            data: 响应数据
            message: 成功信息
            
        Returns:
            成功响应数据字典
        """
        response = {
            'success': True,
            'message': message
        }
        if data is not None:
            response['data'] = data
        return response