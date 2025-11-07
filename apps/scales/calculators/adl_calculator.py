"""
ADL（日常生活能力）量表专用计分器
"""
from typing import Dict, Any, List
from .base import BaseScoreCalculator

class ADLCalculator(BaseScoreCalculator):
    """
    ADL 日常生活能力评定量表计分器
    """
    LEVELS = [
        (20, "完全独立", ["继续保持良好生活习惯"]),
        (40, "轻度依赖", ["建议适当锻炼，保持独立性"]),
        (60, "中度依赖", ["建议家属协助日常活动，关注健康状况"]),
        (100, "重度依赖", ["建议专业护理，密切关注健康变化"]),
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
        return f"您的ADL评分为{score}分，评估结果为：{level}。如有需要，请及时寻求家属或专业帮助。"