"""
MoCA（蒙特利尔认知评估）专用计分器
"""
from typing import Dict, Any, List
from .base import BaseScoreCalculator


class MoCACalculator(BaseScoreCalculator):
    """MoCA（蒙特利尔认知评估）专用计分器"""
    
    THRESHOLD = 26
    EDUCATION_BONUS_YEARS = 12  # 受教育年限≤12年加1分
    
    def calculate(self, selected_options: List[int]) -> Dict[str, Any]:
        raw_score = self._calculate_total_score(selected_options)
        
        # 教育程度校正
        education_years = self._estimate_education_years()
        bonus = 1 if education_years <= self.EDUCATION_BONUS_YEARS else 0
        adjusted_score = min(raw_score + bonus, 30)  # 最高30分
        
        is_abnormal = adjusted_score < self.THRESHOLD
        level = "认知障碍" if is_abnormal else "正常"
        
        return {
            "score": adjusted_score,
            "raw_score": raw_score,
            "education_bonus": bonus,
            "max_score": 30,
            "level": level,
            "is_abnormal": is_abnormal,
            "threshold": self.THRESHOLD,
            "recommendations": self._get_recommendations(is_abnormal),
            "interpretation": self._get_interpretation(raw_score, adjusted_score, is_abnormal)
        }
    
    def _estimate_education_years(self) -> int:
        """估算受教育年限"""
        education = self.user_profile.get('education', '')
        education_years_map = {
            '文盲': 0,
            '小学': 6,
            '初中': 9,
            '高中': 12,
            '中专': 12,
            '大专': 15,
            '本科': 16,
            '硕士': 19,
            '博士': 22,
        }
        for edu_key, years in education_years_map.items():
            if edu_key in education:
                return years
        return 12  # 默认12年
    
    def _get_recommendations(self, is_abnormal: bool) -> List[str]:
        if is_abnormal:
            return [
                "建议进行全面的认知功能评估",
                "咨询神经内科或记忆门诊",
                "定期监测认知功能变化"
            ]
        else:
            return [
                "认知功能正常",
                "建议保持健康生活方式",
                "定期进行认知功能评估"
            ]
    
    def _get_interpretation(self, raw_score: int, adjusted_score: int, is_abnormal: bool) -> str:
        if adjusted_score != raw_score:
            interpretation = f"您的MoCA原始评分为{raw_score}分，教育校正后为{adjusted_score}分。"
        else:
            interpretation = f"您的MoCA评分为{adjusted_score}分。"
        
        if is_abnormal:
            interpretation += f"低于{self.THRESHOLD}分阈值，提示可能存在认知障碍，建议进一步专业评估。"
        else:
            interpretation += "认知功能评估正常。"
        
        return interpretation
