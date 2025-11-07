"""
SCD-Q9（主观认知下降量表）专用计分器
"""
from typing import Dict, Any, List
from .base import BaseScoreCalculator


class SCDCalculator(BaseScoreCalculator):
    """SCD-Q9（主观认知下降量表）专用计分器"""
    
    THRESHOLD = 5  # 判定阈值
    
    def calculate(self, selected_options: List[int]) -> Dict[str, Any]:
        total_score = self._calculate_total_score(selected_options)
        max_score = self._calculate_max_score()
        
        # SCD 特有判定逻辑
        is_abnormal = total_score > self.THRESHOLD
        risk_level = "需进一步评估" if is_abnormal else "正常"
        
        recommendations = []
        if is_abnormal:
            recommendations.extend([
                "建议进行MMSE和MoCA认知功能评估",
                "关注记忆力和认知功能变化",
                "保持规律作息和脑力活动"
            ])
        else:
            recommendations.extend([
                "当前主观认知状态良好",
                "建议保持健康生活方式",
                "定期进行自我评估"
            ])
        
        return {
            "score": total_score,
            "max_score": max_score,
            "level": risk_level,
            "is_abnormal": is_abnormal,
            "threshold": self.THRESHOLD,
            "recommendations": recommendations,
            "next_steps": ["mmse", "moca"] if is_abnormal else [],
            "interpretation": self._get_interpretation(total_score)
        }
    
    def _get_interpretation(self, score: int) -> str:
        if score <= self.THRESHOLD:
            return f"您的SCD-Q9评分为{score}分（≤{self.THRESHOLD}分），未发现明显的主观认知下降，建议保持健康生活方式。"
        else:
            return f"您的SCD-Q9评分为{score}分（>{self.THRESHOLD}分），提示可能存在主观认知下降，建议进行进一步的认知功能评估。"
