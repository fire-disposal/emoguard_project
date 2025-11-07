"""
GAD-7 量表专用计分器
"""
from typing import Dict, Any, List
from .base import BaseScoreCalculator

class GAD7Calculator(BaseScoreCalculator):
    """
    GAD-7 广泛性焦虑量表计分器
    """
    LEVELS = [
        (5, "无/最轻度焦虑", ["继续保持良好心态"]),
        (10, "轻度焦虑", ["建议关注情绪变化，适当放松"]),
        (15, "中度焦虑", ["建议寻求心理咨询，增加社交活动"]),
        (21, "重度焦虑", ["强烈建议及时寻求专业心理帮助"]),
    ]

    def calculate(self, selected_options: List[int]) -> Dict[str, Any]:
        total_score = self._calculate_total_score(selected_options)
        max_score = self._calculate_max_score()
        level, recommendations = self._determine_level(total_score)
        return {
            "score": total_score,
            "max_score": max_score,
            "level": level,
            "recommendations": recommendations,
            "interpretation": self._get_interpretation(total_score, level)
        }

    def _determine_level(self, score: int):
        for threshold, level, recs in self.LEVELS:
            if score < threshold:
                return level, recs
        return self.LEVELS[-1][1], self.LEVELS[-1][2]

    def _get_interpretation(self, score: int, level: str) -> str:
        return f"您的GAD-7评分为{score}分，评估结果为：{level}。如有不适，请及时寻求专业帮助。"