from typing import List, Dict, Any
class BaseScale:
    def __init__(self, *args, **kwargs):
        pass
    name: str
    code: str
    version: str
    description: str
    status: str
    questions: List[Dict]

    def self_check(self) -> Dict[str, Any]:
        """
        自检：检查元数据字段和题目/选项结构语法是否完善
        返回: {"valid": bool, "errors": List[str]}
        """
        errors = []
        # 检查元数据字段
        for field in ["name", "code", "version", "description", "status"]:
            if not getattr(self, field, None):
                errors.append(f"字段缺失: {field}")
        # 检查题目结构
        if not isinstance(self.questions, list) or not self.questions:
            errors.append("questions 必须为非空列表")
        else:
            for idx, q in enumerate(self.questions):
                if not isinstance(q, dict):
                    errors.append(f"第{idx+1}题不是字典类型")
                    continue
                for key in ["id", "text", "options"]:
                    if key not in q:
                        errors.append(f"第{idx+1}题缺少字段: {key}")
                if not isinstance(q.get("options", None), list) or not q.get("options"):
                    errors.append(f"第{idx+1}题 options 必须为非空列表")
        return {"valid": len(errors) == 0, "errors": errors}

    def calculate(self, selected_options: List[int]) -> Dict[str, Any]:
        """
        计算分数和评估结果，需在子类实现
        """
        raise NotImplementedError("请在子类实现具体的评估与计分逻辑")

    def get_question_info(self) -> List[Dict]:
        """
        获取题目及选项结构
        """
        return self.questions

    def get_meta(self) -> Dict[str, Any]:
        """
        获取量表元信息
        """
        return {
            "name": self.name,
            "code": self.code,
            "version": self.version,
            "description": self.description,
            "status": self.status,
        }