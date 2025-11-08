"""
综合判定规则计算器 - 专门处理认知评估流程的最终结论生成
"""
from typing import Dict, Any, Optional
from .base import BaseScoreCalculator
import logging

logger = logging.getLogger(__name__)


class ConclusionCalculator(BaseScoreCalculator):
    """认知评估综合判定计算器"""
    
    # 判定规则配置 - 延续计算器配置思想
    CONCLUSION_RULES = {
        'high_risk': {
            'condition': 'scd_abnormal and mmse_abnormal and moca_abnormal',
            'conclusion': '高风险认知障碍',
            'risk_level': '高风险',
            'recommendations': [
                '强烈建议尽快就医,进行全面的神经心理学评估',
                '咨询神经内科或记忆门诊专家',
                '建立认知功能监测档案',
                '家人应给予更多关注和照护',
                '避免独自外出或操作危险物品'
            ]
        },
        'inconsistent_moca_abnormal': {
            'condition': 'scd_abnormal and not mmse_abnormal and moca_abnormal',
            'conclusion': '可能认知障碍(MoCA提示异常)',
            'risk_level': '中高风险',
            'recommendations': [
                '建议进行更详细的认知功能评估',
                '咨询神经内科或记忆门诊',
                '3-6个月后复查认知功能',
                '保持规律作息和脑力活动',
                '定期监测认知功能变化'
            ]
        },
        'inconsistent_mmse_abnormal': {
            'condition': 'scd_abnormal and mmse_abnormal and not moca_abnormal',
            'conclusion': '可能认知障碍(MMSE提示异常)',
            'risk_level': '中风险',
            'recommendations': [
                '建议进行更详细的认知功能评估',
                '咨询神经内科或记忆门诊',
                '3-6个月后复查认知功能',
                '保持规律作息和脑力活动',
                '定期监测认知功能变化'
            ]
        },
        'subjective_decline': {
            'condition': 'scd_abnormal and not mmse_abnormal and not moca_abnormal',
            'conclusion': '主观认知下降(MCI早期风险提示)',
            'risk_level': '低中风险',
            'recommendations': [
                '建议3-6个月后复查认知功能',
                '保持健康的生活方式',
                '增加脑力活动和社交互动',
                '关注记忆力和认知功能变化',
                '必要时咨询记忆门诊',
                '定期进行认知功能评估'
            ]
        },
        'normal': {
            'condition': 'not scd_abnormal',
            'conclusion': '正常人群',
            'risk_level': '低风险',
            'recommendations': [
                '继续保持健康的生活方式',
                '定期进行认知功能自我评估',
                '保持适度的脑力活动和社交互动'
            ]
        }
    }
    
    def __init__(self, user_profile: Optional[Dict] = None):
        """
        Args:
            user_profile: 用户资料（用于教育程度等校正）
        """
        self.user_profile = user_profile or {}
    
    def calculate(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据各量表分析结果计算综合结论
        
        Args:
            analysis_data: 包含各量表分析结果的字典
                {
                    'scd_q9': scd_analysis,
                    'mmse': mmse_analysis,
                    'moca': moca_analysis
                }
        
        Returns:
            综合判定结果
        """
        # 评估条件
        conditions = self._evaluate_conditions(analysis_data)
        
        # 匹配判定规则
        matched_rule = self._match_conclusion_rule(conditions)
        
        # 构建结论
        return self._build_conclusion(matched_rule, analysis_data, conditions)
    
    def _evaluate_conditions(self, analysis_data: Dict[str, Any]) -> Dict[str, bool]:
        """评估各项条件"""
        scd_analysis = analysis_data.get('scd_q9', {})
        mmse_analysis = analysis_data.get('mmse', {})
        moca_analysis = analysis_data.get('moca', {})
        
        return {
            'scd_abnormal': scd_analysis.get('is_abnormal', False),
            'mmse_abnormal': mmse_analysis.get('is_abnormal', False),
            'moca_abnormal': moca_analysis.get('is_abnormal', False),
            'scd_score': scd_analysis.get('score', 0),
            'mmse_score': mmse_analysis.get('score', 0),
            'moca_score': moca_analysis.get('score', 0)
        }
    
    def _match_conclusion_rule(self, conditions: Dict[str, bool]) -> Optional[Dict[str, Any]]:
        """匹配适用的判定规则"""
        for rule_name, rule_config in self.CONCLUSION_RULES.items():
            if self._evaluate_rule_condition(rule_config['condition'], conditions):
                return rule_config
        return None
    
    def _evaluate_rule_condition(self, condition: str, conditions: Dict[str, bool]) -> bool:
        """评估规则条件"""
        try:
            if condition == 'scd_abnormal and mmse_abnormal and moca_abnormal':
                return conditions['scd_abnormal'] and conditions['mmse_abnormal'] and conditions['moca_abnormal']
            elif condition == 'scd_abnormal and not mmse_abnormal and moca_abnormal':
                return conditions['scd_abnormal'] and not conditions['mmse_abnormal'] and conditions['moca_abnormal']
            elif condition == 'scd_abnormal and mmse_abnormal and not moca_abnormal':
                return conditions['scd_abnormal'] and conditions['mmse_abnormal'] and not conditions['moca_abnormal']
            elif condition == 'scd_abnormal and not mmse_abnormal and not moca_abnormal':
                return conditions['scd_abnormal'] and not conditions['mmse_abnormal'] and not conditions['moca_abnormal']
            elif condition == 'not scd_abnormal':
                return not conditions['scd_abnormal']
            else:
                logger.warning(f"未知的判定条件: {condition}")
                return False
        except Exception as e:
            logger.error(f"评估规则条件失败: {str(e)}")
            return False
    
    def _build_conclusion(self, rule: Optional[Dict[str, Any]], 
                         analysis_data: Dict[str, Any], 
                         conditions: Dict[str, bool]) -> Dict[str, Any]:
        """构建最终结论"""
        if not rule:
            # 默认结论
            return {
                'status': 'completed',
                'conclusion': '需要进一步评估',
                'risk_level': '待评估',
                'summary': '评估结果需要专业医生进一步解读',
                'recommendations': ['建议咨询专业医生'],
                'details': analysis_data
            }
        
        # 个性化总结
        summary = self._generate_summary(rule, conditions, analysis_data)
        
        return {
            'status': 'completed',
            'conclusion': rule['conclusion'],
            'risk_level': rule['risk_level'],
            'summary': summary,
            'recommendations': rule['recommendations'],
            'details': analysis_data,
            'education_corrected': self.user_profile.get('education') if self.user_profile else None
        }
    
    def _generate_summary(self, rule: Dict[str, Any], 
                         conditions: Dict[str, bool], 
                         analysis_data: Dict[str, Any]) -> str:
        """生成个性化总结"""
        scd_score = conditions['scd_score']
        mmse_score = conditions['mmse_score']
        moca_score = conditions['moca_score']
        
        if rule['conclusion'] == '高风险认知障碍':
            return f"SCD-Q9评分{scd_score}分(>5分),MMSE评分{mmse_score}分,MoCA评分{moca_score}分。多项评估提示认知功能障碍。"
        elif rule['conclusion'] == '主观认知下降(MCI早期风险提示)':
            return f"SCD-Q9评分{scd_score}分(>5分),提示主观认知下降,但MMSE({mmse_score}分)和MoCA({moca_score}分)评估暂未发现明显认知障碍。"
        elif '可能认知障碍' in rule['conclusion']:
            return f"SCD-Q9评分{scd_score}分(>5分),MMSE评分{mmse_score}分,MoCA评分{moca_score}分。两项评估结果不一致,建议进一步专业评估。"
        elif rule['conclusion'] == '正常人群':
            return f"SCD-Q9评分{scd_score}分(≤5分),未发现主观认知下降,认知功能正常。"
        
        return "评估完成，请结合临床情况综合判断。"