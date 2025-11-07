"""
MMSE（简易精神状态检查）专用计分器
"""
from typing import Dict, Any, List
from .base import BaseScoreCalculator


class MMSECalculator(BaseScoreCalculator):
    """MMSE（简易精神状态检查）专用计分器"""
    
    # 教育程度校正阈值
    EDUCATION_THRESHOLDS = {
        '文盲': 17,
        '小学': 20,
        '初中': 24,
        '高中': 24,
        '大专': 24,
        '本科': 24,
        '硕士': 24,
        '博士': 24,
    }
    
    def calculate(self, selected_options: List[int]) -> Dict[str, Any]:
        total_score = self._calculate_total_score(selected_options)
        max_score = 30  # MMSE固定30分
        
        # 获取教育程度
        education = self.user_profile.get('education', '初中')
        threshold = self._get_education_threshold(education)
        
        # 判定认知障碍程度
        level = self._determine_level(total_score)
        is_abnormal = total_score <= threshold
        
        return {
            "score": total_score,
            "max_score": max_score,
            "level": level,
            "is_abnormal": is_abnormal,
            "education": education,
            "threshold": threshold,
            "recommendations": self._get_recommendations(level),
            "interpretation": self._get_interpretation(total_score, education, threshold)
        }
    
    def _get_education_threshold(self, education: str) -> int:
        """根据教育程度获取判定阈值"""
        for edu_key, threshold in self.EDUCATION_THRESHOLDS.items():
            if edu_key in education:
                return threshold
        return 24  # 默认初中及以上标准
    
    def _determine_level(self, score: int) -> str:
        """判定认知障碍程度"""
        if score >= 27:
            return "正常"
        elif 21 <= score <= 26:
            return "轻度认知障碍"
        elif 10 <= score <= 20:
            return "中度认知障碍"
        else:
            return "重度认知障碍"
    
    def _get_recommendations(self, level: str) -> List[str]:
        recommendations_map = {
            "正常": ["继续保持良好的生活习惯", "定期进行认知功能评估"],
            "轻度认知障碍": ["建议进行MoCA评估确认", "增加脑力活动", "保持社交互动"],
            "中度认知障碍": ["建议尽快就医进行专业评估", "家人应给予更多关注和照顾"],
            "重度认知障碍": ["强烈建议立即就医", "需要专业医疗干预和全面照护"]
        }
        return recommendations_map.get(level, ["请咨询专业医生"])
    
    def _get_interpretation(self, score: int, education: str, threshold: int) -> str:
        level = self._determine_level(score)
        if score <= threshold:
            return f"根据您的教育程度（{education}），MMSE评分{score}分低于校正阈值{threshold}分，提示{level}，建议进一步评估。"
        else:
            return f"您的MMSE评分为{score}分，认知功能评估结果为{level}。"
