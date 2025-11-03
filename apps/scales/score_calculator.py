"""
量表评分计算器
支持所有YAML配置的量表的统一评分处理
"""
from typing import Dict, Any, List
from datetime import timedelta
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class UniversalScoreCalculator:
    """通用量表评分计算器"""
    
    # 通用分级阈值（百分比）
    RISK_LEVELS = [
        (0.25, '低风险', ['继续保持良好的生活习惯', '定期进行自我评估']),
        (0.50, '轻度风险', ['关注心理健康', '保持规律作息']),
        (0.75, '中度风险', ['建议进行放松训练', '增加社交活动', '定期评估']),
        (1.00, '高风险', ['建议寻求专业心理咨询', '保持规律的作息时间', '密切关注状态变化']),
    ]
    
    @classmethod
    def calculate_total_score(cls, questions: List[Dict], selected_options: List[int]) -> int:
        """
        计算总分 - 通用逻辑
        
        Args:
            questions: 量表题目列表
            selected_options: 用户选择的选项索引列表
            
        Returns:
            总分
        """
        total_score = 0
        
        for idx, question in enumerate(questions):
            try:
                # 获取用户选择的选项索引
                if idx >= len(selected_options):
                    logger.warning(f"题目{idx}没有对应的答案")
                    continue
                    
                selected_idx = selected_options[idx]
                
                # 获取选项
                options = question.get("options", [])
                if selected_idx >= len(options):
                    logger.warning(f"题目{idx}的选项索引{selected_idx}超出范围")
                    continue
                
                option = options[selected_idx]
                
                # 提取value值，支持整数和浮点数
                value = option.get("value", 0)
                
                # 处理字符串类型value
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
    
    @classmethod
    def calculate_max_score(cls, questions: List[Dict]) -> int:
        """
        计算最大可能分数
        
        Args:
            questions: 量表题目列表
            
        Returns:
            最大分数
        """
        max_score = 0
        
        for question in questions:
            options = question.get("options", [])
            if not options:
                continue
            
            # 找到该题目中最大的value
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
    
    @classmethod
    def determine_risk_level(cls, total_score: int, max_score: int) -> tuple:
        """
        根据总分和最大分确定风险等级
        
        Args:
            total_score: 总分
            max_score: 最大分
            
        Returns:
            (风险等级, 建议列表)
        """
        if max_score == 0:
            return '未知', ['无法计算风险等级']
        
        percentage = total_score / max_score
        
        for threshold, level, recommendations in cls.RISK_LEVELS:
            if percentage < threshold:
                return level, recommendations
        
        # 如果超过所有阈值，返回最高级别
        return cls.RISK_LEVELS[-1][1], cls.RISK_LEVELS[-1][2]
    
    @classmethod
    def generate_analysis(cls, total_score: int, max_score: int, scale_type: str) -> Dict[str, Any]:
        """
        生成评估结果分析
        
        Args:
            total_score: 总分
            max_score: 最大分
            scale_type: 量表类型
            
        Returns:
            分析结果JSON
        """
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        risk_level, recommendations = cls.determine_risk_level(total_score, max_score)
        
        analysis = {
            "total_score": total_score,
            "max_score": max_score,
            "risk_level": risk_level,
            "percentage": round(percentage, 2),
            "recommendations": recommendations,
            "interpretation": cls._get_interpretation(risk_level, scale_type),
            "next_assessment_date": cls._get_next_assessment_date()
        }
        
        return analysis
    
    @classmethod
    def _get_interpretation(cls, risk_level: str, scale_type: str) -> str:
        """获取结果解释"""
        interpretations = {
            '低风险': f'您的{scale_type}评估结果显示为低风险，请继续保持良好的生活状态。',
            '轻度风险': f'您的{scale_type}评估结果显示为轻度风险，建议关注您的心理健康。',
            '中度风险': f'您的{scale_type}评估结果显示为中度风险，建议进行适当的调整并定期评估。',
            '高风险': f'您的{scale_type}评估结果显示为高风险，强烈建议您寻求专业帮助。',
        }
        return interpretations.get(risk_level, '请咨询专业人士获取详细解释。')
    
    @classmethod
    def _get_next_assessment_date(cls) -> str:
        """获取下次评估建议日期（30天后）"""
        return (timezone.now() + timedelta(days=30)).date().isoformat()


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


def calculate_score_by_instance(scale_config, scale_result) -> Dict[str, Any]:
    """
    根据量表配置和结果计算分数
    支持所有YAML量表的统一处理
    
    Args:
        scale_config: ScaleConfig实例
        scale_result: ScaleResult实例
        
    Returns:
        分析结果JSON
    """
    questions = scale_config.questions
    selected_options = scale_result.selected_options
    scale_type = scale_config.type
    
    # 验证有效性
    validation = validate_assessment(
        questions, 
        selected_options, 
        scale_result.started_at, 
        scale_result.completed_at
    )
    
    # 计算分数
    calculator = UniversalScoreCalculator()
    total_score = calculator.calculate_total_score(questions, selected_options)
    max_score = calculator.calculate_max_score(questions)
    
    # 生成分析
    analysis = calculator.generate_analysis(total_score, max_score, scale_type)
    
    # 添加验证结果
    analysis["validation"] = validation
    
    logger.info(f"量表{scale_config.code}评分完成: 总分{total_score}/{max_score}, 风险{analysis['risk_level']}")
    
    return analysis