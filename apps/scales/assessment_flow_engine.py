"""
认知评估流程引擎
处理 SCD→MMSE/MoCA 的条件判定和综合分析
"""
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class CognitiveAssessmentFlowEngine:
    """认知评估流程引擎"""
    
    # 流程定义
    FLOW_STEPS = {
        'step1': {
            'name': '主观认知下降筛查',
            'scales': ['scd_q9'],
            'required': True
        },
        'step2': {
            'name': '认知功能评估',
            'scales': ['mmse', 'moca'],
            'required': False,  # 根据SCD结果决定
            'condition': 'scd_abnormal'
        }
    }
    
    def __init__(self, result_group):
        """
        Args:
            result_group: AssessmentResultGroup实例
        """
        self.result_group = result_group
        self.results_cache = {}  # 缓存已完成的量表结果
    
    def get_next_step(self) -> Dict[str, Any]:
        """
        获取下一步应该完成的量表
        
        Returns:
            {
                'completed': bool,  # 流程是否已完成
                'next_scales': List[str],  # 下一步需要完成的量表代码列表
                'reason': str  # 原因说明
            }
        """
        # 获取已完成的量表
        completed_scales = self._get_completed_scales()
        
        # Step 1: 检查SCD是否完成
        if 'scd_q9' not in completed_scales:
            return {
                'completed': False,
                'next_scales': ['scd_q9'],
                'reason': '请先完成主观认知下降量表(SCD-Q9)初筛',
                'step': 'step1'
            }
        
        # Step 2: 根据SCD结果决定是否需要MMSE/MoCA
        scd_result = self.results_cache.get('scd_q9')
        if not scd_result:
            return {
                'completed': False,
                'next_scales': ['scd_q9'],
                'reason': 'SCD-Q9结果异常,请重新评估',
                'step': 'step1'
            }
        
        scd_abnormal = scd_result.analysis.get('is_abnormal', False)
        
        if not scd_abnormal:
            # SCD正常,流程完成
            return {
                'completed': True,
                'next_scales': [],
                'reason': 'SCD-Q9评分正常,暂无认知障碍风险,不需要进一步评估',
                'step': 'completed'
            }
        
        # SCD异常,需要MMSE和MoCA
        needed_scales = []
        if 'mmse' not in completed_scales:
            needed_scales.append('mmse')
        if 'moca' not in completed_scales:
            needed_scales.append('moca')
        
        if needed_scales:
            return {
                'completed': False,
                'next_scales': needed_scales,
                'reason': 'SCD-Q9提示认知下降,建议完成MMSE和MoCA评估',
                'step': 'step2'
            }
        
        # 所有量表已完成
        return {
            'completed': True,
            'next_scales': [],
            'reason': '认知评估流程已完成',
            'step': 'completed'
        }
    
    def _get_completed_scales(self) -> List[str]:
        """获取已完成的量表代码列表"""
        from .models import ScaleResult
        
        results = ScaleResult.objects.filter(
            result_group=self.result_group
        ).select_related('scale_config')
        
        completed = []
        for result in results:
            scale_code = result.scale_config.code.lower()
            completed.append(scale_code)
            self.results_cache[scale_code] = result
        
        return completed
    
    def generate_comprehensive_analysis(self, user_profile: Optional[Dict] = None) -> Dict[str, Any]:
        """
        生成综合分析结果
        
        Args:
            user_profile: 用户资料(包含教育程度等)
            
        Returns:
            综合分析结果
        """
        completed_scales = self._get_completed_scales()
        
        # 必须完成SCD
        if 'scd_q9' not in completed_scales:
            return {
                'status': 'incomplete',
                'message': '未完成SCD-Q9评估'
            }
        
        scd_result = self.results_cache['scd_q9']
        scd_analysis = scd_result.analysis
        scd_abnormal = scd_analysis.get('is_abnormal', False)
        
        # 如果SCD正常,直接返回
        if not scd_abnormal:
            return {
                'status': 'completed',
                'conclusion': '正常人群',
                'risk_level': '低风险',
                'summary': f"SCD-Q9评分{scd_analysis['score']}分(≤5分),未发现主观认知下降,认知功能正常。",
                'recommendations': [
                    '继续保持健康的生活方式',
                    '定期进行认知功能自我评估',
                    '保持适度的脑力活动和社交互动'
                ],
                'details': {
                    'scd_q9': scd_analysis
                }
            }
        
        # SCD异常,需要MMSE和MoCA
        if 'mmse' not in completed_scales or 'moca' not in completed_scales:
            return {
                'status': 'incomplete',
                'message': 'SCD-Q9提示异常,需完成MMSE和MoCA评估',
                'details': {
                    'scd_q9': scd_analysis
                }
            }
        
        # 获取MMSE和MoCA结果
        mmse_result = self.results_cache['mmse']
        moca_result = self.results_cache['moca']
        mmse_analysis = mmse_result.analysis
        moca_analysis = moca_result.analysis
        
        # 综合判定
        final_conclusion = self._determine_final_conclusion(
            scd_analysis, 
            mmse_analysis, 
            moca_analysis,
            user_profile
        )
        
        return {
            'status': 'completed',
            'conclusion': final_conclusion['conclusion'],
            'risk_level': final_conclusion['risk_level'],
            'summary': final_conclusion['summary'],
            'recommendations': final_conclusion['recommendations'],
            'details': {
                'scd_q9': scd_analysis,
                'mmse': mmse_analysis,
                'moca': moca_analysis
            },
            'education_corrected': user_profile.get('education') if user_profile else None
        }
    
    def _determine_final_conclusion(
        self, 
        scd_analysis: Dict, 
        mmse_analysis: Dict, 
        moca_analysis: Dict,
        user_profile: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        综合判定最终结论
        
        判定规则:
        1. SCD > 5 且 MMSE、MoCA 均异常 → 高风险认知障碍
        2. SCD > 5 且 MMSE、MoCA 结果不一致 → 可能认知障碍(优先采纳MoCA)
        3. SCD > 5 但 MMSE、MoCA 均正常 → 主观认知下降(MCI早期风险)
        """
        mmse_abnormal = mmse_analysis.get('is_abnormal', False)
        moca_abnormal = moca_analysis.get('is_abnormal', False)
        
        # 情况1: 两个都异常
        if mmse_abnormal and moca_abnormal:
            return {
                'conclusion': '高风险认知障碍',
                'risk_level': '高风险',
                'summary': f"SCD-Q9评分{scd_analysis['score']}分(>5分),MMSE评分{mmse_analysis['score']}分({mmse_analysis['level']}),MoCA评分{moca_analysis['score']}分(异常)。多项评估提示认知功能障碍。",
                'recommendations': [
                    '强烈建议尽快就医,进行全面的神经心理学评估',
                    '咨询神经内科或记忆门诊专家',
                    '建立认知功能监测档案',
                    '家人应给予更多关注和照护',
                    '避免独自外出或操作危险物品'
                ]
            }
        
        # 情况2: 结果不一致(优先采纳MoCA)
        if mmse_abnormal != moca_abnormal:
            if moca_abnormal:
                conclusion = '可能认知障碍(MoCA提示异常)'
                risk_level = '中高风险'
            else:
                conclusion = '可能认知障碍(MMSE提示异常)'
                risk_level = '中风险'
            
            return {
                'conclusion': conclusion,
                'risk_level': risk_level,
                'summary': f"SCD-Q9评分{scd_analysis['score']}分(>5分),MMSE评分{mmse_analysis['score']}分,MoCA评分{moca_analysis['score']}分。两项评估结果不一致,建议进一步专业评估。",
                'recommendations': [
                    '建议进行更详细的认知功能评估',
                    '咨询神经内科或记忆门诊',
                    '3-6个月后复查认知功能',
                    '保持规律作息和脑力活动',
                    '定期监测认知功能变化'
                ]
            }
        
        # 情况3: 两个都正常但SCD异常
        return {
            'conclusion': '主观认知下降(MCI早期风险提示)',
            'risk_level': '低中风险',
            'summary': f"SCD-Q9评分{scd_analysis['score']}分(>5分),提示主观认知下降,但MMSE({mmse_analysis['score']}分)和MoCA({moca_analysis['score']}分)评估暂未发现明显认知障碍,可能处于MCI早期阶段。",
            'recommendations': [
                '建议3-6个月后复查认知功能',
                '保持健康的生活方式',
                '增加脑力活动和社交互动',
                '关注记忆力和认知功能变化',
                '必要时咨询记忆门诊',
                '定期进行认知功能评估'
            ]
        }

def select_latest_scale_by_type(self, scale_type: str):
    """
    根据 type 字段选用最高版本的量表
    :param scale_type: 量表类型（如 SCD、MMSE、MoCA）
    :return: ScaleConfig 实例或 None
    """
    from .models import ScaleConfig
    return ScaleConfig.objects.filter(type=scale_type, status='active').order_by('-version').first()

def cognitive_assessment_flow(self, user_id):
    """
    认知评估流程自动推进与判定
    """
    # 1. SCD-Q9
    scd_scale = self.select_latest_scale_by_type('SCD')
    scd_result = self.get_user_scale_result(user_id, scd_scale)
    if scd_result is None:
        return {'next': 'SCD-Q9', 'status': 'pending'}
    if scd_result.total_score <= 5:
        return {'conclusion': '正常', 'next': None}
    # 2. MMSE
    mmse_scale = self.select_latest_scale_by_type('MMSE')
    mmse_result = self.get_user_scale_result(user_id, mmse_scale)
    if mmse_result is None:
        return {'next': 'MMSE', 'status': 'pending'}
    # 3. MoCA
    moca_scale = self.select_latest_scale_by_type('MoCA')
    moca_result = self.get_user_scale_result(user_id, moca_scale)
    if moca_result is None:
        return {'next': 'MoCA', 'status': 'pending'}
    # 综合判定（略，按业务规则实现）
    return self.cognitive_conclusion(scd_result, mmse_result, moca_result)
