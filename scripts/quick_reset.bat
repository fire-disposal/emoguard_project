@echo off
REM Django项目快速重置脚本
REM 用于快速清理迁移和重建数据库

echo.
echo ========================================
echo Django项目快速重置工具
echo ========================================
echo.

REM 检查是否在项目根目录
if not exist "manage.py" (
    echo 错误: 请在Django项目根目录运行此脚本
    pause
    exit /b 1
)

REM 停止正在运行的服务
echo 停止Django服务...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

REM 运行清理脚本
echo.
echo 开始清理和重建数据库...
python scripts/clean_migrations.py

if %errorlevel% neq 0 (
    echo.
    echo 错误: 清理过程失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 重置完成！
echo 你可以现在运行: python manage.py runserver
echo ========================================
echo.

pause