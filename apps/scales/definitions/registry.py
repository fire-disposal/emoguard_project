import importlib
import pkgutil

from apps.scales.definitions.base import BaseScale

class ScaleRegistry:
    _registry = {}

    @classmethod
    def discover_scales(cls, package="apps.scales.definitions"):
        """自动发现所有量表定义类并注册（仅注册BaseScale子类），异常安全"""
        cls._registry.clear()
        pkg = importlib.import_module(package)
        for _, modname, ispkg in pkgutil.iter_modules(pkg.__path__):
            if ispkg:
                continue
            try:
                module = importlib.import_module(f"{package}.{modname}")
                for attr in dir(module):
                    obj = getattr(module, attr)
                    if (
                        isinstance(obj, type)
                        and issubclass(obj, BaseScale)
                        and obj is not BaseScale
                        and hasattr(obj, "code")
                        and hasattr(obj, "questions")
                    ):
                        # 自检功能，提前发现量表定义错误
                        try:
                            check_result = obj().self_check()
                            if not check_result["valid"]:
                                import logging
                                logging.getLogger(__name__).error(
                                    f"量表插件 {modname}.{obj.__name__} 自检失败: {check_result['errors']}"
                                )
                                continue  # 跳过有错误的量表
                        except Exception as ce:
                            import logging
                            logging.getLogger(__name__).error(
                                f"量表插件 {modname}.{obj.__name__} 自检异常: {ce}", exc_info=True
                            )
                            continue
                        cls._registry[obj.code] = obj
            except Exception as e:
                # 插件解析异常，记录但不中断整体流程
                import logging
                logging.getLogger(__name__).error(f"量表插件 {modname} 加载失败: {e}", exc_info=True)

    @classmethod
    def get_scale(cls, code):
        """返回量表实例（无用户信息）"""
        scale_cls = cls._registry.get(code)
        if scale_cls:
            return scale_cls()
        return None

    @classmethod
    def all_scales(cls):
        """返回所有量表类（可用于批量实例化）"""
        return [cls._registry[k] for k in cls._registry]

    @classmethod
    def get_questions(cls, code):
        """获取指定量表的题目结构"""
        scale_cls = cls._registry.get(code)
        if scale_cls:
            return scale_cls().get_question_info()
        return []

    @classmethod
    def calculate(cls, code, selected_options):
        """直接调用量表的评估/计分逻辑"""
        scale = cls.get_scale(code)
        if scale:
            return scale.calculate(selected_options)
        return {"error": "量表或评估逻辑不存在"}