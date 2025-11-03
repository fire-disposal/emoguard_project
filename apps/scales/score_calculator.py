from typing import Dict, Any
from datetime import timedelta
from django.utils import timezone
from .models import ScaleConfig, ScaleResult

def calculate_mmse_score(questions, selected_options) -> int:
    """
    计算 MMSE 量表的总分
    """
    total_score = 0
    for idx, question in enumerate(questions):
        try:
            selected_idx = selected_options[idx]
            option = question["options"][selected_idx]
            value = option.get("value", 0)
            total_score += value
        except Exception:
            continue
    return total_score

def mmse_analysis(score: int, question_count: int) -> Dict[str, Any]:
    """
    综合分析 MMSE 结果，返回分级、建议、详细分析等
    """
    if question_count == 0:
        level = "未知"
        recommendations = []
        details = {}
    else:
        percent = score / (2 * question_count)
        if percent >= 0.8:
            level = "低风险"
            recommendations = ["继续保持良好的生活习惯", "定期进行自我评估"]
            details = {"记忆力": percent, "生活自理": 1.0}
        elif percent >= 0.5:
            level = "中风险"
            recommendations = ["建议进行放松训练", "增加社交活动"]
            details = {"记忆力": percent, "生活自理": 0.5}
        elif percent >= 0.25:
            level = "高风险"
            recommendations = ["建议寻求专业心理咨询", "保持规律的作息时间"]
            details = {"记忆力": percent, "生活自理": 0.2}
        else:
            level = "极高风险"
            recommendations = ["建议寻求专业心理咨询", "保持规律的作息时间"]
            details = {"记忆力": percent, "生活自理": 0.1}
    return {
        "level": level,
        "recommendations": recommendations,
        "detailed_analysis": details
    }

def get_next_assessment_date() -> str:
    return (timezone.now() + timedelta(days=30)).date().isoformat()

def calculate_score_by_instance(scale_config: ScaleConfig, scale_result: ScaleResult) -> Dict[str, Any]:
    scale_type = scale_config.type
    questions = scale_config.questions
    selected_options = scale_result.selected_options

    if scale_type == "MMSE":
        score = calculate_mmse_score(questions, selected_options)
        analysis = mmse_analysis(score, len(questions))
        next_assessment_date = get_next_assessment_date()
        return {
            "score": score,
            "level": analysis["level"],
            "recommendations": analysis["recommendations"],
            "detailed_analysis": analysis["detailed_analysis"],
            "next_assessment_date": next_assessment_date
        }
    # 可扩展其它量表类型
    score = sum(selected_options) if selected_options else 0
    return {
        "score": score,
        "level": "未知",
        "recommendations": [],
        "detailed_analysis": {},
        "next_assessment_date": get_next_assessment_date()
    }