from ninja_extra import NinjaExtraAPI
from django.urls import path
from ninja_jwt.controller import NinjaJWTDefaultController
from apps.users.views import users_router
from apps.articles.views import articles_router
from apps.journals.views import journals_router
from apps.reports.views import reports_router
from apps.scales.views import scales_router
from apps.notifications.views import notifications_router
from apps.emotiontracker.views import emotion_router
from apps.feedback.views import feedback_router

# 使用NinjaExtraAPI替代普通的NinjaAPI以支持django-ninja-jwt
# Django Ninja 框架已经内置了完善的异常处理机制，无需自定义异常处理器
api = NinjaExtraAPI(
    title="认知照顾情绪监测系统 API",
    version="1.0.0",
    description="认知照顾情绪监测系统的后端API，支持用户管理、文章管理、情绪日记、健康报告、量表评估等功能",
    csrf=True,
    # Django Ninja 会自动处理以下异常：
    # - ValidationError: 返回 422 状态码
    # - Http404: 返回 404 状态码
    # - 其他异常: 返回 500 状态码
)

# 注册JWT控制器 - django-ninja-jwt会自动提供以下端点：
# POST /api/token/pair/ - 获取令牌对（访问令牌+刷新令牌）
# POST /api/token/refresh/ - 刷新访问令牌
# POST /api/token/verify/ - 验证令牌
api.register_controllers(NinjaJWTDefaultController)

api.add_router("/users", users_router)
api.add_router("/articles", articles_router)
api.add_router("/journals", journals_router)
api.add_router("/reports", reports_router)
api.add_router("/scales", scales_router)
api.add_router("/notifications", notifications_router)
api.add_router("/emotiontracker", emotion_router)
api.add_router("/feedback", feedback_router)

urlpatterns = [
    path("", api.urls),
]