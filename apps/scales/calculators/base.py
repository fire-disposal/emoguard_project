"""
基础计分器 - 所有计分器的父类
"""
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class BaseScoreCalculator:
    """基础计分器 - 所有计分器的父类"""
    
    def __init__(self, scale_config, user_profile: Optional[Dict] = None):
        """
        Args:
            scale_config: ScaleConfig实例
            user_profile: 用户资料（用于教育程度等校正）
        """
        self.scale_config = scale_config
        self.user_profile = user_profile or {}
        self.questions = scale_config.questions
        self.scale_type = scale_config.type
        self.scale_code = scale_config.code
    
    def calculate(self, selected_options: List[int]) -> Dict[str, Any]:
        """计算分数和分析结果 - 子类必须实现"""
        raise NotImplementedError("子类必须实现calculate方法")
    
    def _calculate_total_score(self, selected_options: List[int]) -> int:
        """计算总分"""
        total_score = 0
        for idx, question in enumerate(self.questions):
            try:
                if idx >= len(selected_options):
                    logger.warning(f"题目{idx}没有对应的答案")
                    continue
                    
                selected_idx = selected_options[idx]
                options = question.get("options", [])
                if selected_idx >= len(options):
                    logger.warning(f"题目{idx}的选项索引{selected_idx}超出范围")
                    continue
                
                option = options[selected_idx]
                value = option.get("value", 0)
                
                if isinstance(value, str):
                    try:
                        value = float(value)
                    except ValueError:
                        logger.warning(f"题目{idx}的value '{value}' 无法转换为数字，使用0")
                        value = 0
                
                total_score += value
            except Exception as e:
                logger.error(f"计算题目{idx}分数时出错: {str(e)}")
                continue
        
        return int(total_score)
    
    def _calculate_max_score(self) -> int:
        """计算最大可能分数"""
        max_score = 0
        for question in self.questions:
            options = question.get("options", [])
            if not options:
                continue
            max_value = 0
            for option in options:
                value = option.get("value", 0)
                if isinstance(value, str):
                    try:
                        value = float(value)
                    except ValueError:
                        value = 0
                max_value = max(max_value, value)
            max_score += max_value
        return int(max_score)
