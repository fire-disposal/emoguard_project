"""
通用量表计分器 - 用于不需要特殊逻辑的量表
"""
from typing import Dict, Any, List
from .base import BaseScoreCalculator


class UniversalScoreCalculator(BaseScoreCalculator):
    """通用量表评分计算器 - 用于不需要特殊逻辑的量表"""
    
    RISK_LEVELS = [
        (0.25, '低风险', ['继续保持良好的生活习惯', '定期进行自我评估']),
        (0.50, '轻度风险', ['关注心理健康', '保持规律作息']),
        (0.75, '中度风险', ['建议进行放松训练', '增加社交活动', '定期评估']),
        (1.00, '高风险', ['建议寻求专业心理咨询', '保持规律的作息时间', '密切关注状态变化']),
    ]
    
    def calculate(self, selected_options: List[int]) -> Dict[str, Any]:
        total_score = self._calculate_total_score(selected_options)
        max_score = self._calculate_max_score()
        
        percentage = (total_score / max_score) if max_score > 0 else 0
        risk_level, recommendations = self._determine_risk_level(percentage)
        
        return {
            "score": total_score,
            "max_score": max_score,
            "level": risk_level,
            "percentage": round(percentage * 100, 2),
            "recommendations": recommendations,
            "interpretation": self._get_interpretation(risk_level)
        }
    
    def _determine_risk_level(self, percentage: float) -> tuple:
        for threshold, level, recommendations in self.RISK_LEVELS:
            if percentage < threshold:
                return level, recommendations
        return self.RISK_LEVELS[-1][1], self.RISK_LEVELS[-1][2]
    
    def _get_interpretation(self, risk_level: str) -> str:
        interpretations = {
            '低风险': f'您的{self.scale_type}评估结果显示为低风险，请继续保持良好的生活状态。',
            '轻度风险': f'您的{self.scale_type}评估结果显示为轻度风险，建议关注您的心理健康。',
            '中度风险': f'您的{self.scale_type}评估结果显示为中度风险，建议进行适当的调整并定期评估。',
            '高风险': f'您的{self.scale_type}评估结果显示为高风险，强烈建议您寻求专业帮助。',
        }
        return interpretations.get(risk_level, '请咨询专业人士获取详细解释。')
