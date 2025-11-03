from django.http import JsonResponse
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

def health_info_view(request):
    return JsonResponse({
        "system_name": "认知照顾情绪监测系统",
        "version": "1.0.0"
    }, json_dumps_params={'ensure_ascii': False})

urlpatterns = [
    path('', health_info_view, name='root'),  # 根路径处理
    path('admin/', admin.site.urls),
    path('api/', include('config.api')),  # Ninja API统一路由
    path('summernote/', include('django_summernote.urls')),  # 富文本编辑器
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)