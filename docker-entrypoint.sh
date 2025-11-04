#!/bin/bash
set -e

echo "🚀 启动 EmoGuard 后端服务..."

# ============================
# ✅ 等数据库就绪（PostgreSQL）
# ============================
echo "⏳ 等待数据库连接..."
timeout=60
while ! .venv/bin/python - <<EOF 2>/dev/null
import os, psycopg2
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
EOF
do
    timeout=$((timeout - 1))
    if [ $timeout -eq 0 ]; then
        echo "❌ 数据库连接超时"
        exit 1
    fi
    echo "  等待数据库连接... ($timeout 秒剩余)"
    sleep 1
done
echo "✅ 数据库连接成功"

# ============================
# ✅ 执行数据库迁移
# ============================
echo "🔄 执行数据库迁移..."
.venv/bin/python manage.py migrate --noinput

# ============================
# ✅ 创建超级用户（如果配置了环境变量）
# ============================
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "👤 创建超级用户..."
    .venv/bin/python manage.py create_admin
else
    echo "ℹ️ 未设置超级用户环境变量，跳过创建"
fi

# ============================
# ✅ 加载量表配置（如存在）
# ============================
if [ -d "apps/scales/yaml_configs" ]; then
    echo "📊 加载量表配置..."
    .venv/bin/python manage.py load_scales_from_yaml
fi

# ============================
# ✅ 收集静态文件（生产环境临时 + 容器外挂载目录）
# ============================
# 修复静态文件收集权限问题
mkdir -p /app/staticfiles
chmod -R 777 /app/staticfiles
echo "📁 收集静态文件..."
.venv/bin/python manage.py collectstatic --noinput

echo "✅ 初始化完成，启动应用..."

# 最后执行 CMD 命令（gunicorn）
exec "$@"
