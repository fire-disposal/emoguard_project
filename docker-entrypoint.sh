#!/bin/bash
set -e

# ============================
# 欢迎 Banner
# ============================
cat << 'EMOGUARD_BANNER'
  ______                  _____                     _ 
 |  ____|                / ____|                   | |
 | |__   _ __ ___   ___ | |  __ _   _  __ _ _ __ __| |
 |  __| | '_ ` _ \ / _ \| | |_ | | | |/ _` | '__/ _` |
 | |____| | | | | | (_) | |__| | |_| | (_| | | | (_| |
 |______|_| |_| |_|\___/ \_____|\__,_|\__,_|_|  \__,_|                                                                                                                     
EMOGUARD_BANNER

echo "🚀 启动 EmoGuard 后端服务..."

# ============================
# ✅ 执行数据库迁移
# ============================
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
# ✅ 收集静态文件（生产环境临时 + 容器外挂载目录）
# ============================
# 修复静态文件收集权限问题
mkdir -p /app/staticfiles
chmod -R 777 /app/staticfiles
echo "📁 收集静态文件..."
uv run python manage.py collectstatic --noinput

echo "✅ 初始化完成，启动应用..."

# ============================
# ✅ 创建定时任务
# ============================
echo "🔄 创建定时任务..."
uv run python manage.py setup_periodic_tasks

# ============================
# ✅ 启动 Celery Worker（后台）
# ============================
echo "🔄 启动 Celery Worker..."
nohup uv run celery -A apps.notice worker -l info -Q notice > /app/logs/celery-worker.log 2>&1 &

# ============================
# ✅ 启动 Celery Beat（后台）
# ============================
echo "🔄 启动 Celery Beat..."
nohup uv run celery -A apps.notice beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler > /app/logs/celery-beat.log 2>&1 &

echo "✅ Celery 服务已启动"

# 最后执行 CMD 命令（gunicorn）
exec "$@"
