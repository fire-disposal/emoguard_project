from ninja_extra import NinjaExtraAPI
from django.urls import path
from ninja_jwt.controller import NinjaJWTDefaultController
from apps.users.views import users_router
from apps.articles.views import articles_router
from apps.journals.views import journals_router
from apps.reports.views import reports_router
from apps.scales.views import scales_router

# 使用NinjaExtraAPI替代普通的NinjaAPI以支持django-ninja-jwt
api = NinjaExtraAPI(title="认知照顾情绪监测系统 API", version="1.0.0")

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

urlpatterns = [
    path("", api.urls),
]