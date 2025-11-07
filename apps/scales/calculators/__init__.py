"""
量表计分器模块
每种量表类型对应一个独立的计分器文件
"""
from .base import BaseScoreCalculator
from .scd_calculator import SCDCalculator
from .mmse_calculator import MMSECalculator
from .moca_calculator import MoCACalculator
from .phq9_calculator import PHQ9Calculator
from .gad7_calculator import GAD7Calculator
from .adl_calculator import ADLCalculator
from .sus_calculator import SUSCalculator
from .emotiontest_calculator import EmotionTestCalculator

__all__ = [
    'BaseScoreCalculator',
    'SCDCalculator',
    'MMSECalculator',
    'MoCACalculator',
    'PHQ9Calculator',
    'GAD7Calculator',
    'ADLCalculator',
    'SUSCalculator',
    'EmotionTestCalculator',
    'get_calculator',
]


def get_calculator(scale_config, user_profile=None):
    """
    工厂方法：根据量表代码返回对应的计分器
    
    Args:
        scale_config: ScaleConfig实例
        user_profile: 用户资料字典（可选）
        
    Returns:
        计分器实例
    """
    calculator_map = {
        'scd_q9': SCDCalculator,
        'mmse': MMSECalculator,
        'moca': MoCACalculator,
        'phq9': PHQ9Calculator,
        'gad7': GAD7Calculator,
        'adl': ADLCalculator,
        'sus': SUSCalculator,
        'emotiontest': EmotionTestCalculator,
    }

    scale_code = scale_config.code.lower()
    calculator_class = calculator_map.get(scale_code)
    if calculator_class is None:
        raise NotImplementedError(f"请为量表 {scale_code} 实现专用计分器")
    return calculator_class(scale_config, user_profile)
