#!/bin/bash
# Django项目快速重置脚本
# 用于快速清理迁移和重建数据库

echo ""
echo "========================================"
echo "Django项目快速重置工具"
echo "========================================"
echo ""

# 检查是否在项目根目录
if [ ! -f "manage.py" ]; then
    echo "错误: 请在Django项目根目录运行此脚本"
    read -p "按任意键退出..."
    exit 1
fi

# 停止正在运行的服务
echo "停止Django服务..."
pkill -f "python manage.py runserver" 2>/dev/null
sleep 2

# 运行清理脚本
echo ""
echo "开始清理和重建数据库..."
python scripts/clean_migrations.py

if [ $? -ne 0 ]; then
    echo ""
    echo "错误: 清理过程失败"
    read -p "按任意键退出..."
    exit 1
fi

echo ""
echo "========================================"
echo "重置完成！"
echo "你可以现在运行: python manage.py runserver"
echo "========================================"
echo ""

read -p "按任意键退出..."