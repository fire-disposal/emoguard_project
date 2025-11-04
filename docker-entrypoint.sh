#!/bin/bash
set -e

echo "🚀 启动 EmoGuard 后端服务..."

# 等待数据库就绪
echo "⏳ 等待数据库连接..."
timeout=60
while ! python -c "import psycopg2; psycopg2.connect(os.environ.get('DATABASE_URL'))" 2>/dev/null; do
    timeout=$((timeout - 1))
    if [ $timeout -eq 0 ]; then
        echo "❌ 数据库连接超时"
        exit 1
    fi
    echo "  等待数据库连接... ($timeout 秒剩余)"
    sleep 1
done
echo "✅ 数据库连接成功"

# 执行数据库迁移
echo "🔄 执行数据库迁移..."
.venv/bin/python manage.py migrate --noinput

# 创建超级用户（如果不存在）
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "👤 创建超级用户..."
    .venv/bin/python manage.py create_admin

# 加载量表数据（如果存在YAML配置）
if [ -d "apps/scales/yaml_configs" ]; then
    echo "📊 加载量表配置..."
    .venv/bin/python manage.py load_scales_from_yaml
fi

# 收集静态文件（生产环境）
echo "📁 收集静态文件..."
.venv/bin/python manage.py collectstatic --noinput --clear

echo "✅ 初始化完成，启动应用..."

# 执行传入的命令
exec "$@"