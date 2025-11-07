"""
SUS（系统可用性量表）专用计分器
"""
from typing import Dict, Any, List
from .base import BaseScoreCalculator

class SUSCalculator(BaseScoreCalculator):
    """
    SUS 系统可用性量表计分器
    """
    def calculate(self, selected_options: List[int]) -> Dict[str, Any]:
        # SUS 特有计分规则：奇数题(正向)为选项分数-1，偶数题(反向)为5-选项分数
        total_score = 0
        for idx, selected_idx in enumerate(selected_options):
            # SUS 题目编号从1开始
            if (idx + 1) % 2 == 1:
                total_score += selected_idx + 1 - 1
            else:
                total_score += 5 - (selected_idx + 1)
        sus_score = total_score * 2.5  # SUS 总分标准化到100分
        level = self._get_level(sus_score)
        return {
            "score": sus_score,
            "max_score": 100,
            "level": level,
            "interpretation": self._get_interpretation(sus_score, level)
        }

    def _get_level(self, score: float) -> str:
        if score >= 85:
            return "卓越"
        elif score >= 70:
            return "良好"
        elif score >= 50:
            return "一般"
        else:
            return "较差"

    def _get_interpretation(self, score: float, level: str) -> str:
        return f"您的SUS评分为{score:.1f}分，系统可用性评价为：{level}。"