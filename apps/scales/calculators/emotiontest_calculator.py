"""
EmotionTest 情绪识别量表专用计分器
"""
from typing import Dict, Any, List
from .base import BaseScoreCalculator

class EmotionTestCalculator(BaseScoreCalculator):
    """
    情绪识别能力评定量表计分器
    """
    LEVELS = [
        (5, "较弱", ["建议多练习情绪识别，提高情绪理解能力"]),
        (8, "一般", ["建议关注他人情绪变化，提升共情能力"]),
        (12, "良好", ["情绪识别能力较好，建议继续保持"]),
        (100, "优秀", ["情绪识别能力优秀，继续保持积极心态"]),
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
        return f"您的情绪识别评分为{score}分，能力评价为：{level}。"