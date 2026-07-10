from django.http import JsonResponse
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .health import health_check
from .token_views import token_refresh_slash

def health_info_view(request):
    return JsonResponse({
        "system_name": "认知照顾情绪监测系统",
        "version": "1.0.0",
        "健康检查路由":"/health",
        "管理页路由":"/admin",
        "接口路由":"/api",
        "接口文档":"/api/docs",
    }, json_dumps_params={'ensure_ascii': False})

urlpatterns = [
    path('', health_info_view, name='root'),  # 根路径处理
    path('health/', health_check, name='health'),  # 健康检查
    path('admin/', admin.site.urls),
    # 带尾斜杠的令牌刷新，须在 api/ include 之前以优先匹配小程序请求
    path('api/token/refresh/', token_refresh_slash, name='token_refresh_slash'),
    path('api/', include('config.api')),  # Ninja API统一路由
    path('summernote/', include('django_summernote.urls')),  # 富文本编辑器
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)