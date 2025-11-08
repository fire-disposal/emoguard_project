"""
量表评分计算器
模块化设计：针对不同量表类型提供专用计分器
"""
from typing import Dict, Any, List, Optional
from .calculators import get_calculator
import logging

logger = logging.getLogger(__name__)

def validate_assessment(questions: List[Dict], selected_options: List[int], 
                       started_at, completed_at) -> Dict[str, Any]:
    """
    验证评估有效性
    
    Args:
        questions: 题目列表
        selected_options: 用户选择
        started_at: 开始时间
        completed_at: 完成时间
        
    Returns:
        验证结果
    """
    warnings = []
    is_valid = True
    
    # 检查答题完整性
    if len(selected_options) != len(questions):
        warnings.append(f"答题不完整：应答{len(questions)}题，实际答{len(selected_options)}题")
        is_valid = False
    
    # 检查答题时长
    duration = (completed_at - started_at).total_seconds()
    min_duration = len(questions) * 2  # 每题至少2秒
    
    if duration < min_duration:
        warnings.append(f"答题时间过短：{duration:.0f}秒，可能影响结果准确性")
    
    # 检查选项有效性
    for idx, selected_idx in enumerate(selected_options):
        if idx < len(questions):
            options_count = len(questions[idx].get("options", []))
            if selected_idx >= options_count or selected_idx < 0:
                warnings.append(f"题目{idx+1}的选项索引{selected_idx}无效")
                is_valid = False
    
    return {
        "is_valid": is_valid,
        "warnings": warnings
    }


def calculate_score_by_instance(scale_config, scale_result, user_profile: Optional[Dict] = None) -> Dict[str, Any]:
    """
    根据量表配置和结果计算分数（模块化版本）
    
    Args:
        scale_config: ScaleConfig实例
        scale_result: ScaleResult实例
        user_profile: 用户资料字典（可选）
        
    Returns:
        分析结果JSON
    """
    selected_options = scale_result.selected_options
    
    # 验证有效性
    validation = validate_assessment(
        scale_config.questions, 
        selected_options, 
        scale_result.started_at, 
        scale_result.completed_at
    )
    
    # 使用模块化计分器
    calculator = get_calculator(scale_config, user_profile)
    analysis = calculator.calculate(selected_options)
    
    # 添加验证结果和元数据
    analysis["validation"] = validation
    analysis["scale_code"] = scale_config.code
    analysis["scale_name"] = scale_config.name
    
    logger.info(f"量表{scale_config.code}评分完成: 总分{analysis['score']}/{analysis.get('max_score', 'N/A')}, 等级{analysis['level']}")
    
    return analysis