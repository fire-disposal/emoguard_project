from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import time

def health_check(request):
    """健康检查接口"""
    start_time = time.time()
    
    # 检查数据库连接
    db_status = "healthy"
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # 检查缓存
    cache_status = "healthy"
    try:
        cache.set('health_check', 'ok', 30)
        if cache.get('health_check') != 'ok':
            cache_status = "unhealthy: cache test failed"
    except Exception as e:
        cache_status = f"unhealthy: {str(e)}"
    
    response_time = round((time.time() - start_time) * 1000, 2)
    
    status = "healthy"
    if db_status != "healthy" or cache_status != "healthy":
        status = "unhealthy"
    
    return JsonResponse({
        "status": status,
        "timestamp": int(time.time()),
        "response_time_ms": response_time,
        "checks": {
            "database": db_status,
            "cache": cache_status
        }
    })