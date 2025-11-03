#!/usr/bin/env python
"""
Django迁移清理脚本
用于清理所有迁移文件并重建数据库
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def run_command(command, description=""):
    """运行shell命令并处理错误"""
    print(f"\n{'='*60}")
    print(f"执行: {description or command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误: {e}")
        if e.stdout:
            print(f"输出: {e.stdout}")
        if e.stderr:
            print(f"错误输出: {e.stderr}")
        return False

def clean_migrations():
    """清理所有迁移文件"""
    print("开始清理迁移文件...")
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    apps_dir = project_root / "apps"
    
    # 清理每个app的迁移文件
    migration_files_cleaned = 0
    
    if apps_dir.exists():
        for app_dir in apps_dir.iterdir():
            if app_dir.is_dir():
                migrations_dir = app_dir / "migrations"
                if migrations_dir.exists():
                    # 保留 __init__.py 文件，删除其他迁移文件
                    for migration_file in migrations_dir.iterdir():
                        if migration_file.name != "__init__.py" and migration_file.suffix == ".py":
                            try:
                                migration_file.unlink()
                                migration_files_cleaned += 1
                                print(f"删除: {migration_file}")
                            except Exception as e:
                                print(f"删除失败 {migration_file}: {e}")
                    
                    # 删除 __pycache__ 目录
                    pycache_dir = migrations_dir / "__pycache__"
                    if pycache_dir.exists():
                        try:
                            shutil.rmtree(pycache_dir)
                            print(f"删除: {pycache_dir}")
                        except Exception as e:
                            print(f"删除失败 {pycache_dir}: {e}")
    
    print(f"\n清理完成！共删除 {migration_files_cleaned} 个迁移文件")
    return True

def clean_database():
    """清理数据库文件"""
    print("\n开始清理数据库...")
    
    project_root = Path(__file__).parent.parent
    db_file = project_root / "db.sqlite3"
    
    if db_file.exists():
        try:
            db_file.unlink()
            print(f"删除数据库文件: {db_file}")
            return True
        except Exception as e:
            print(f"删除数据库失败: {e}")
            return False
    else:
        print("数据库文件不存在，跳过删除")
        return True

def create_migrations():
    """创建新的迁移文件"""
    print("\n开始创建新的迁移文件...")
    
    # 先创建所有app的迁移
    if not run_command("python manage.py makemigrations", "创建迁移文件"):
        return False
    
    return True

def migrate_database():
    """执行迁移"""
    print("\n开始执行数据库迁移...")
    
    if not run_command("python manage.py migrate", "执行数据库迁移"):
        return False
    
    return True

def create_superuser():
    """创建超级用户"""
    print("\n创建超级用户...")
    
    # 检查是否已存在超级用户
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if not User.objects.filter(is_superuser=True).exists():
        return run_command("python manage.py createsuperuser", "创建超级用户")
    else:
        print("超级用户已存在，跳过创建")
        return True

def collect_static():
    """收集静态文件"""
    print("\n收集静态文件...")
    return run_command("python manage.py collectstatic --noinput", "收集静态文件")

def main():
    """主函数"""
    print("Django迁移清理和重建工具")
    print("=" * 60)
    
    # 检查是否在项目根目录
    manage_py = Path("manage.py")
    if not manage_py.exists():
        print("错误: 请在Django项目根目录运行此脚本")
        sys.exit(1)
    
    # 步骤1: 清理迁移文件
    if not clean_migrations():
        print("清理迁移文件失败")
        sys.exit(1)
    
    # 步骤2: 清理数据库
    if not clean_database():
        print("清理数据库失败")
        sys.exit(1)
    
    # 步骤3: 创建新的迁移文件
    if not create_migrations():
        print("创建迁移文件失败")
        sys.exit(1)
    
    # 步骤4: 执行迁移
    if not migrate_database():
        print("数据库迁移失败")
        sys.exit(1)
    
    # 步骤5: 收集静态文件
    if not collect_static():
        print("收集静态文件失败")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("所有操作完成！数据库已清理并重建。")
    print("你可以现在运行: python manage.py runserver")
    print("=" * 60)

if __name__ == "__main__":
    main()