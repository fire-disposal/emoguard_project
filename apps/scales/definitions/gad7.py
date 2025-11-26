from typing import List, Dict, Any
from apps.scales.definitions.base import BaseScale

class GAD7Scale(BaseScale):
    name = "广泛性焦虑障碍量表-7项 (GAD-7)"
    code = "GAD-7"
    version = "1.0"
    description = "广泛性焦虑障碍筛查量表"
    type = "GAD"
    status = "active"
    questions: List[Dict] = [
        {
            "id": 1,
            "text": "感觉紧张，焦虑或急切。",
            "options": [
                {"text": "完全不会", "value": "0"},
                {"text": "好几天", "value": "1"},
                {"text": "超过一周", "value": "2"},
                {"text": "几乎每天", "value": "3"},
            ],
        },
        {
            "id": 2,
            "text": "对各种各样的事情担忧过多。",
            "options": [
                {"text": "完全不会", "value": "0"},
                {"text": "好几天", "value": "1"},
                {"text": "超过一周", "value": "2"},
                {"text": "几乎每天", "value": "3"},
            ],
        },
        {
            "id": 3,
            "text": "担心过多不同的事情。",
            "options": [
                {"text": "完全不会", "value": "0"},
                {"text": "好几天", "value": "1"},
                {"text": "超过一周", "value": "2"},
                {"text": "几乎每天", "value": "3"},
            ],
        },
        {
            "id": 4,
            "text": "很难放松下来。",
            "options": [
                {"text": "完全不会", "value": "0"},
                {"text": "好几天", "value": "1"},
                {"text": "超过一周", "value": "2"},
                {"text": "几乎每天", "value": "3"},
            ],
        },
        {
            "id": 5,
            "text": "坐立不安，难以静坐。",
            "options": [
                {"text": "完全不会", "value": "0"},
                {"text": "好几天", "value": "1"},
                {"text": "超过一周", "value": "2"},
                {"text": "几乎每天", "value": "3"},
            ],
        },
        {
            "id": 6,
            "text": "容易恼怒或烦躁。",
            "options": [
                {"text": "完全不会", "value": "0"},
                {"text": "好几天", "value": "1"},
                {"text": "超过一周", "value": "2"},
                {"text": "几乎每天", "value": "3"},
            ],
        },
        {
            "id": 7,
            "text": "担心会发生某些可怕的事情。",
            "options": [
                {"text": "完全不会", "value": "0"},
                {"text": "好几天", "value": "1"},
                {"text": "超过一周", "value": "2"},
                {"text": "几乎每天", "value": "3"},
            ],
        },
    ]

    LEVELS = [
        (5, "无/最轻度焦虑", ["继续保持良好心态"]),
        (10, "轻度焦虑", ["建议关注情绪变化，适当放松"]),
        (15, "中度焦虑", ["建议寻求心理咨询，增加社交活动"]),
        (21, "重度焦虑", ["强烈建议及时寻求专业心理帮助"]),
    ]

    def calculate(self, selected_options: List[int]) -> Dict[str, Any]:
        total_score = 0
        answers = []
        for idx, question in enumerate(self.questions):
            answer_info = {
                "question_id": question.get("id"),
                "question_text": question.get("text"),
                "selected_option": None,
                "selected_text": None,
                "value": 0,
            }
            if idx < len(selected_options):
                opt_idx = selected_options[idx]
                options = question.get("options", [])
                if 0 <= opt_idx < len(options):
                    option = options[opt_idx]
                    value = option.get("value", 0)
                    try:
                        value = float(value)
                    except Exception:
                        value = 0
                    total_score += value
                    answer_info["selected_option"] = opt_idx
                    answer_info["selected_text"] = option.get("text", "")
                    answer_info["value"] = value
            answers.append(answer_info)
        level, recommendations = self._determine_level(total_score)
        return {
            "score": total_score,
            "max_score": self._calculate_max_score(),
            "level": level,
            "recommendations": recommendations,
            "interpretation": self._get_interpretation(total_score, level),
            "answers": answers,
        }

    def _determine_level(self, score: float):
        for threshold, level, recs in self.LEVELS:
            if score < threshold:
                return level, recs
        return self.LEVELS[-1][1], self.LEVELS[-1][2]

    def _calculate_max_score(self) -> float:
        max_score = 0
        for question in self.questions:
            options = question.get("options", [])
            max_value = max([float(opt.get("value", 0)) for opt in options], default=0)
            max_score += max_value
        return max_score

    def _get_interpretation(self, score: float, level: str) -> str:
        return f"您的GAD-7评分为{score}分，评估结果为：{level}。如有不适，请及时寻求专业帮助。"