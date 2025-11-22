#!/bin/bash


set -e

# =================================================================
# 📋 容器角色判断和初始化逻辑
# =================================================================

# 从环境变量获取容器角色，默认为 'backend'
CONTAINER_ROLE="${CONTAINER_ROLE:-backend}"

echo "==================================================="
echo "🚀 Starting Container - Role: $CONTAINER_ROLE"
echo "==================================================="

# -----------------------------------------------------------------
# 🔍 数据库连接等待 (Application Level Wait)
# 
# 尽管 docker-compose 依赖已设置，但应用层需确认数据库服务可接受连接。
# -----------------------------------------------------------------
echo "⏳ Waiting for PostgreSQL connection to be ready..."
MAX_ATTEMPTS=20 # 减少到 20 次，总共 40 秒，避免过长等待
ATTEMPTS=0
until [ $ATTEMPTS -ge $MAX_ATTEMPTS ]; do
    # 使用 Django 的 check 命令来验证数据库连接
    if uv run python manage.py check --database default > /dev/null 2>&1; then
        echo "✅ Database connection established."
        break
    fi

    ATTEMPTS=$((ATTEMPTS + 1))
    echo "   Attempt $ATTEMPTS/$MAX_ATTEMPTS: Waiting for DB..."
    sleep 2
done

# 如果循环结束仍未成功连接，则退出
if [ $ATTEMPTS -eq $MAX_ATTEMPTS ]; then
    echo "❌ Failed to connect to database after $MAX_ATTEMPTS attempts."
    exit 1
fi


# -----------------------------------------------------------------
# 🔄 主后端容器执行初始化操作 (仅由 backend 容器执行)
# -----------------------------------------------------------------
if [ "$CONTAINER_ROLE" = "backend" ]; then
    echo "--- Initializing Backend Service ---"

    # 1. 数据库迁移
    echo "🔄 Running database migrations..."
    uv run python manage.py migrate --noinput
    
    # 2. 收集静态文件 (运行一次)
    echo "📁 Collecting static files..."
    uv run python manage.py collectstatic --noinput
    
    # 3. 创建超级用户
    if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
        echo "👤 Creating or ensuring superuser exists..."
        # 确保 create_admin 是幂等的 (只创建不存在的用户)
        uv run python manage.py create_admin
    else
        echo "ℹ️ DJANGO_SUPERUSER_USERNAME not set. Skipping superuser creation."
    fi
    
    # 4. 加载量表配置
    if [ -d "apps/scales/yaml_configs" ]; then
        echo "📊 Loading scale configurations from YAML..."
        uv run python manage.py load_scales_from_yaml
    fi
    
    # 5. 创建定时任务
    echo "🗓️ Setting up periodic tasks..."
    uv run python manage.py setup_periodic_tasks
    
    echo "✅ Backend initialization complete."
fi

# -----------------------------------------------------------------
# 🏃 根据容器角色执行相应命令 (使用 exec 确保信号处理)
# -----------------------------------------------------------------
echo "---------------------------------------------------"
case "$CONTAINER_ROLE" in
    "worker")
        echo "// [🔄️ Starting Celery Worker] //"
        # 确保 worker 使用了正确的 app 名称和日志级别
        exec uv run celery -A apps.notice worker -l info -Q notice
        ;;
    "beat")
        echo "// [❤️ Starting Celery Beat] //"
        # 确保 beat 使用了正确的 app 名称和调度器
        exec uv run celery -A apps.notice beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
        ;;
    "backend")
        echo "// [🌱 Starting Gunicorn Backend] //"
        
        # Banner 展示
        cat << 'EMOGUARD_BANNER'

                       _oo0oo_
                      o8888888o
                      88" . "88
                      (| -_- |)
                      0\  =  /0
                    ___/`---'\___
                  .' \\|     |// '.
                 / \\|||  :  |||// \
                / _||||| -:- |||||- \
               |   | \\\  - /// |   |
               | \_|  ''\---/''  |_/ |
               \  .-\__  '-'  ___/-. /
             ___'. .'  /--.--\  `. .'___
          ."" '<  `.___\_<|>_/___.' >' "".
         | | :  `- \`.;`\ _ /`;.`/ - ` : | |
         \  \ `_.   \_ __\ /__ _/   .-` /  /
     =====`-.____`.___ \_____/___.-`___.-'=====
                       `=---='

           佛祖保佑     永不宕机     永无BUG

  ______                  _____                     _ 
 |  ____|                / ____|                   | |
 | |__   _ __ ___   ___ | |  __ _   _  __ _ _ __ __| |
 |  __| | '_ ` _ \ / _ \| | |_ | | | |/ _` | '__/ _` |
 | |____| | | | | | (_) | |__| | |_| | (_| | | | (_| |
 |______|_| |_| |_|\___/ \_____|\__,_|\__,_|_|  \__,_|
                                                                                      
EMOGUARD_BANNER
        
        # 使用 exec 启动 Gunicorn
        exec uv run gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 --keep-alive 5 --max-requests 1000 --max-requests-jitter 100 config.wsgi:application
        ;;
    *)
        echo "⚠️ Unknown container role: $CONTAINER_ROLE. Executing default command."
        exec "$@"
        ;;
esac