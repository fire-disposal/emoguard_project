from typing import List, Dict

class CognitiveAssessmentScoringService:
    """
    评分服务：根据选项计算得分与分析（可后续扩展）
    """
    @staticmethod
    def calculate_score(scale_config, selected_options: List[int]) -> Dict:
        # TODO: 实现评分逻辑，可复用/简化 apps.scales.services.scale_result_service
        # 这里只返回示例结构
        return {
            "score": sum(selected_options),
            "analysis": {
                "score": sum(selected_options),
                "level": "示例",
                "is_abnormal": False,
                "recommendations": []
            }
        }