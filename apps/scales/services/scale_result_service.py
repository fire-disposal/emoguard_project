"""
量表结果服务 - 处理量表结果相关业务逻辑
"""
from typing import Optional, Dict, Any
from datetime import datetime
from django.shortcuts import get_object_or_404
from apps.scales.models import ScaleResult, ScaleConfig
from apps.scales.score_calculator import calculate_score_by_instance
from apps.scales.services.user_service import UserService
import logging

logger = logging.getLogger(__name__)


class ScaleResultService:
    """量表结果服务类 - 处理量表结果的创建和计算"""
    
    @staticmethod
    def create_scale_result(
        user_id: str,
        scale_config_id: int,
        selected_options: list,
        duration_ms: int,
        started_at: str,
        completed_at: str,
        user_profile: Optional[Dict] = None
    ) -> Optional[ScaleResult]:
        """
        创建量表结果
        
        Args:
            user_id: 用户ID
            scale_config_id: 量表配置ID
            selected_options: 选择的选项
            duration_ms: 用时（毫秒）
            started_at: 开始时间
            completed_at: 完成时间
            user_profile: 用户资料
            
        Returns:
            量表结果实例或None
        """
        try:
            # 获取量表配置
            scale_config = get_object_or_404(ScaleConfig, id=scale_config_id)
            
            # 如果未提供用户资料，尝试获取
            if user_profile is None:
                user_profile = UserService.get_user_profile(user_id)
            
            # 标准化时间格式
            started_dt = datetime.fromisoformat(started_at)
            completed_dt = datetime.fromisoformat(completed_at)
            
            # 验证和修正时长
            calculated_duration = int((completed_dt - started_dt).total_seconds() * 1000)
            if calculated_duration != duration_ms:
                logger.info(f"修正答题时长: {duration_ms}ms -> {calculated_duration}ms")
                duration_ms = calculated_duration
            
            # 创建临时对象用于计算
            temp_result = ScaleResult(
                user_id=user_id,
                scale_config=scale_config,
                selected_options=selected_options,
                duration_ms=duration_ms,
                started_at=started_dt,
                completed_at=completed_dt,
                status='completed'
            )
            
            # 计算分数和分析
            analysis = calculate_score_by_instance(
                scale_config, 
                temp_result, 
                user_profile
            )
            
            # 构建结论摘要
            conclusion = ScaleResultService._build_conclusion(analysis)
            
            # 创建量表结果
            result = ScaleResult.objects.create(
                user_id=user_id,
                scale_config=scale_config,
                selected_options=selected_options,
                conclusion=conclusion,
                duration_ms=duration_ms,
                started_at=started_dt,
                completed_at=completed_dt,
                status='completed',
                analysis=analysis
            )
            
            logger.info(f"量表结果创建成功: 用户{user_id}, 量表{scale_config.code}, 分数{analysis.get('score', 'N/A')}")
            return result
            
        except Exception as e:
            logger.error(f"创建量表结果失败: {str(e)}")
            return None
    
    @staticmethod
    def create_grouped_scale_result(
        group,
        scale_config_id: int,
        selected_options: list,
        duration_ms: int,
        started_at: str,
        completed_at: str,
        user_profile: Optional[Dict] = None
    ) -> Optional[ScaleResult]:
        """
        创建分组量表结果
        
        Args:
            group: 评估结果分组
            scale_config_id: 量表配置ID
            selected_options: 选择的选项
            duration_ms: 用时（毫秒）
            started_at: 开始时间
            completed_at: 完成时间
            user_profile: 用户资料
            
        Returns:
            量表结果实例或None
        """
        try:
            # 获取量表配置
            scale_config = get_object_or_404(ScaleConfig, id=scale_config_id)
            
            # 如果未提供用户资料，尝试获取
            if user_profile is None:
                user_profile = UserService.get_user_profile(group.user_id)
            
            # 标准化时间格式
            started_dt = datetime.fromisoformat(started_at)
            completed_dt = datetime.fromisoformat(completed_at)
            
            # 验证和修正时长
            calculated_duration = int((completed_dt - started_dt).total_seconds() * 1000)
            if calculated_duration != duration_ms:
                logger.info(f"修正答题时长: {duration_ms}ms -> {calculated_duration}ms")
                duration_ms = calculated_duration
            
            # 创建临时对象用于计算
            temp_result = ScaleResult(
                user_id=group.user_id,
                scale_config=scale_config,
                selected_options=selected_options,
                duration_ms=duration_ms,
                started_at=started_dt,
                completed_at=completed_dt,
                status='completed'
            )
            
            # 计算分数和分析
            analysis = calculate_score_by_instance(
                scale_config, 
                temp_result, 
                user_profile
            )
            
            # 构建结论摘要
            conclusion = ScaleResultService._build_conclusion(analysis)
            
            # 创建量表结果并关联到分组
            result = ScaleResult.objects.create(
                user_id=group.user_id,
                scale_config=scale_config,
                result_group=group,
                selected_options=selected_options,
                conclusion=conclusion,
                duration_ms=duration_ms,
                started_at=started_dt,
                completed_at=completed_dt,
                status='completed',
                analysis=analysis
            )
            
            logger.info(f"分组量表结果创建成功: 分组{group.id}, 量表{scale_config.code}, 分数{analysis.get('score', 'N/A')}")
            return result
            
        except Exception as e:
            logger.error(f"创建分组量表结果失败: {str(e)}")
            return None
    
    @staticmethod
    def _build_conclusion(analysis: Dict[str, Any]) -> str:
        """
        构建结论摘要
        
        Args:
            analysis: 分析结果
            
        Returns:
            结论摘要字符串
        """
        try:
            score = analysis.get('score', 'N/A')
            level = analysis.get('level', 'N/A')
            
            # 根据不同量表类型构建不同的结论格式
            if 'is_abnormal' in analysis:
                abnormal_status = "异常" if analysis['is_abnormal'] else "正常"
                return f"分值:{score} 分级:{level} 状态:{abnormal_status}"
            else:
                return f"分值:{score} 分级:{level}"
                
        except Exception as e:
            logger.error(f"构建结论摘要失败: {str(e)}")
            return f"分值:{analysis.get('score', 'N/A')} 分级:{analysis.get('level', 'N/A')}"
    
    @staticmethod
    def get_user_scale_results(user_id: str, limit: int = 10) -> list:
        """
        获取用户的量表结果列表
        
        Args:
            user_id: 用户ID
            limit: 限制数量
            
        Returns:
            量表结果列表
        """
        try:
            return list(ScaleResult.objects.filter(
                user_id=user_id
            ).select_related('scale_config').order_by('-created_at')[:limit])
        except Exception as e:
            logger.error(f"获取用户量表结果失败: {str(e)}")
            return []
    
    @staticmethod
    def get_scale_result_by_id(result_id: int) -> Optional[ScaleResult]:
        """
        根据ID获取量表结果
        
        Args:
            result_id: 结果ID
            
        Returns:
            量表结果实例或None
        """
        try:
            return ScaleResult.objects.select_related('scale_config').get(id=result_id)
        except ScaleResult.DoesNotExist:
            logger.warning(f"量表结果 {result_id} 不存在")
            return None
        except Exception as e:
            logger.error(f"获取量表结果失败: {str(e)}")
            return None