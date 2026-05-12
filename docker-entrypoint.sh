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
# -----------------------------------------------------------------
echo "⏳ Waiting for PostgreSQL connection to be ready..."
MAX_ATTEMPTS=20
ATTEMPTS=0
until [ $ATTEMPTS -ge $MAX_ATTEMPTS ]; do
    if uv run python manage.py check --database default > /dev/null 2>&1; then
        echo "✅ Database connection established."
        break
    fi
    ATTEMPTS=$((ATTEMPTS + 1))
    echo "   Attempt $ATTEMPTS/$MAX_ATTEMPTS: Waiting for DB..."
    sleep 2
done

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
    
    # 2. 收集静态文件
    echo "📁 Collecting static files..."
    uv run python manage.py collectstatic --noinput
    
    # 3. 创建超级用户
    if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
        echo "👤 Creating or ensuring superuser exists..."
        uv run python manage.py create_admin
    else
        echo "ℹ️ DJANGO_SUPERUSER_USERNAME not set. Skipping superuser creation."
    fi
    
    # 4. 加载量表配置
    if [ -d "apps/scales/yaml_configs" ]; then
        echo "📊 Loading scale configurations from YAML..."
        uv run python manage.py load_scales_from_yaml
    fi
    
    echo "✅ Backend initialization complete."
fi

# -----------------------------------------------------------------
# 🏃 根据容器角色执行相应命令
# -----------------------------------------------------------------
echo "---------------------------------------------------"
case "$CONTAINER_ROLE" in
    "backend")
        echo "// [🌱 Starting Gunicorn + Scheduler] //"
        
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
        
        # 启动轻量级调度器 (后台)
        uv run python manage.py run_scheduler &
        
        # 启动 Gunicorn (前台，阻塞)
        exec uv run gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 --keep-alive 5 --max-requests 1000 --max-requests-jitter 100 config.wsgi:application
        ;;
    *)
        echo "⚠️ Unknown container role: $CONTAINER_ROLE. Executing default command."
        exec "$@"
        ;;
esac
