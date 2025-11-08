"""
流程步骤计算器 - 专门处理评估流程的下一步判定
"""
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class FlowStepCalculator:
    """评估流程步骤计算器"""
    
    # 流程步骤配置 - 计算器化思想
    FLOW_STEPS = {
        'step1': {
            'name': '主观认知下降筛查',
            'scales': ['scd_q9'],
            'required': True,
            'next_evaluator': 'evaluate_scd_completion'
        },
        'step2': {
            'name': '认知功能评估', 
            'scales': ['mmse'],
            'required': False,
            'condition': 'scd_abnormal',
            'next_evaluator': 'evaluate_cognitive_completion'
        }
    }
    
    def calculate_next_step(self, completed_scales: List[str], 
                           scale_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算下一步需要完成的量表
        
        Args:
            completed_scales: 已完成的量表代码列表
            scale_results: 量表结果缓存
            
        Returns:
            下一步步骤信息
        """
        # Step 1: 检查SCD完成情况
        if 'scd_q9' not in completed_scales:
            return self._build_step_response(
                completed=False,
                next_scales=['scd_q9'],
                reason='请先完成主观认知下降量表(SCD-Q9)初筛',
                step='step1'
            )
        
        # 评估SCD结果
        scd_result = scale_results.get('scd_q9')
        if not scd_result:
            return self._build_step_response(
                completed=False,
                next_scales=['scd_q9'],
                reason='SCD-Q9结果异常,请重新评估',
                step='step1'
            )
        
        scd_abnormal = scd_result.get('is_abnormal', False)
        
        if not scd_abnormal:
            # SCD正常，流程完成
            return self._build_step_response(
                completed=True,
                next_scales=[],
                reason='SCD-Q9评分正常,暂无认知障碍风险',
                step='completed'
            )
        
        # SCD异常，需要MMSE和MoCA
        needed_scales = []
        for scale in ['mmse', 'moca']:
            if scale not in completed_scales:
                needed_scales.append(scale)
        
        if needed_scales:
            return self._build_step_response(
                completed=False,
                next_scales=needed_scales,
                reason='SCD-Q9提示认知下降,建议完成MMSE和MoCA评估',
                step='step2'
            )
        
        # 所有量表已完成
        return self._build_step_response(
            completed=True,
            next_scales=[],
            reason='认知评估流程已完成',
            step='completed'
        )
    
    def _build_step_response(self, completed: bool, next_scales: List[str], 
                            reason: str, step: str) -> Dict[str, Any]:
        """构建步骤响应"""
        return {
            'completed': completed,
            'next_scales': next_scales,
            'reason': reason,
            'step': step
        }
    
    def evaluate_scd_completion(self, scd_analysis: Dict[str, Any]) -> bool:
        """
        评估SCD完成情况
        
        Args:
            scd_analysis: SCD分析结果
            
        Returns:
            是否完成
        """
        return scd_analysis.get('is_abnormal') is not None
    
    def evaluate_cognitive_completion(self, mmse_analysis: Dict[str, Any], 
                                    moca_analysis: Dict[str, Any]) -> bool:
        """
        评估认知功能完成情况
        
        Args:
            mmse_analysis: MMSE分析结果
            moca_analysis: MoCA分析结果
            
        Returns:
            是否完成
        """
        return (mmse_analysis.get('is_abnormal') is not None and 
                moca_analysis.get('is_abnormal') is not None)