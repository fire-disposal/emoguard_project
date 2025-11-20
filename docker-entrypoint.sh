#!/bin/bash
set -e

# ============================
# ✅ 容器角色判断和初始化逻辑
# ============================

# 获取容器角色（从环境变量判断，默认为backend）
CONTAINER_ROLE="${CONTAINER_ROLE:-backend}"

echo "📋 容器角色: $CONTAINER_ROLE"

# 只有主后端容器执行完整的初始化操作
if [ "$CONTAINER_ROLE" = "backend" ]; then
    echo "🔄 执行数据库迁移..."
    uv run python manage.py migrate --noinput
    
    # ============================
    # ✅ 创建超级用户（如果配置了环境变量）
    # ============================
    if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
        echo "👤 创建超级用户..."
        uv run python manage.py create_admin
    else
        echo "ℹ️ 未设置超级用户环境变量，跳过创建"
    fi
    
    # ============================
    # ✅ 加载量表配置（如存在）
    # ============================
    if [ -d "apps/scales/yaml_configs" ]; then
        echo "📊 加载量表配置..."
        uv run python manage.py load_scales_from_yaml
    fi
    
    # ============================
    # ✅ 收集静态文件
    # ============================
    echo "📁 收集静态文件..."
    uv run python manage.py collectstatic --noinput
    
    # ============================
    # ✅ 创建定时任务
    # ============================
    echo "🔄 创建定时任务..."
    uv run python manage.py setup_periodic_tasks
    
    echo "✅ 主后端容器初始化完成，启动应用..."
else
    # Worker和Beat容器等待数据库就绪
    echo "⏳ Worker/Beat容器等待数据库就绪..."
    for i in {1..30}; do
        if uv run python manage.py check --database default > /dev/null 2>&1; then
            echo "✅ 数据库连接正常"
            break
        fi
        echo "⏳ 等待数据库连接... ($i/30)"
        sleep 2
    done
    
    # 简单的健康检查，确保基本表结构存在
    echo "🔍 检查数据库基本状态..."
    uv run python manage.py check --database default > /dev/null 2>&1 || {
        echo "❌ 数据库未就绪，等待主后端容器完成初始化"
        sleep 10
    }
    
    echo "✅ Worker/Beat容器初始化完成，启动应用..."
    fi
    
    # ============================
    # ✅ 根据容器角色执行相应命令
    # ============================
    case "$CONTAINER_ROLE" in
        "worker")
            echo "// [🔄️ 启动 Celery Worker]-------------------------//"
            exec uv run celery -A apps.notice worker -l info -Q notice
            ;;
        "beat")
            echo "// [❤️ 启动 Celery Beat]-------------------------//"
            exec uv run celery -A apps.notice beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
            ;;
        "backend")
            echo "// [🌱 启动 Backend 后端]-------------------------//"
            
            #banner展示
            cat << 'EMOGUARD_BANNER'
  ______                  _____                     _ 
 |  ____|                / ____|                   | |
 | |__   _ __ ___   ___ | |  __ _   _  __ _ _ __ __| |
 |  __| | '_ ` _ \ / _ \| | |_ | | | |/ _` | '__/ _` |
 | |____| | | | | | (_) | |__| | |_| | (_| | | | (_| |
 |______|_| |_| |_|\___/ \_____|\__,_|\__,_|_|  \__,_|                                                                                                                     
EMOGUARD_BANNER
            exec uv run gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 --keep-alive 5 --max-requests 1000 --max-requests-jitter 100 config.wsgi:application
            ;;
        *)
            echo "⚠️ 未知的容器角色: $CONTAINER_ROLE，执行默认命令"
            exec "$@"
            ;;
    esac