# 快速启动指南

本指南帮助您快速启动重构后的系统。

## 前置要求

- Python 3.11+
- pip包管理器

## 启动步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
pip install Pillow  # ImageField需要
```

### 2. 数据库迁移

**重要：执行迁移前请先备份数据库！**

```bash
# 创建迁移文件
python manage.py makemigrations

# 执行迁移
python manage.py migrate
```

### 3. 创建管理员账号

```bash
python manage.py createsuperuser
```

按提示输入管理员信息：
- 用户名（username）
- 邮箱（可选）
- 密码（至少8位）

### 4. 加载量表配置

```bash
python manage.py load_scales_from_yaml
```

这将从 `apps/scales/yaml_configs/` 目录加载所有YAML量表配置。

### 5. 创建媒体目录

```bash
mkdir -p media/articles/covers
```

### 6. 启动开发服务器

```bash
python manage.py runserver
```

服务器将在 http://localhost:8000 启动。

### 7. 访问API文档

打开浏览器访问：http://localhost:8000/api/docs

您将看到完整的API文档和交互式测试界面。

## 测试API

### 1. 管理员登录

```bash
curl -X POST http://localhost:8000/api/users/admin/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_admin_username",
    "password": "your_password"
  }'
```

响应示例：
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "...",
    "username": "admin",
    "role": "admin",
    ...
  }
}
```

### 2. 使用令牌访问受保护资源

```bash
curl http://localhost:8000/api/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. 创建情绪日记

```bash
curl -X POST http://localhost:8000/api/journals/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mood_score": 7,
    "text": "今天心情不错",
    "record_date": "2025-11-03T15:30:00+08:00"
  }'
```

### 4. 获取通知列表

```bash
curl http://localhost:8000/api/notifications/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 配置微信小程序

### 1. 设置环境变量

在项目根目录创建 `.env` 文件（可选）：

```env
WECHAT_MINI_PROGRAM_APP_ID=your_app_id
WECHAT_MINI_PROGRAM_APP_SECRET=your_app_secret
```

### 2. 或直接修改settings.py

编辑 `config/settings.py`：

```python
WECHAT_MINI_PROGRAM_APP_ID = 'your_app_id'
WECHAT_MINI_PROGRAM_APP_SECRET = 'your_app_secret'
```

### 3. 测试微信登录

```bash
curl -X POST http://localhost:8000/api/users/wechat/login \
  -H "Content-Type: application/json" \
  -d '{
    "code": "wx_login_code_from_miniprogram"
  }'
```

## 常见问题

### Q: 迁移失败

**解决方案：**
1. 确保已安装所有依赖
2. 检查数据库连接
3. 查看具体错误信息

### Q: ImageField报错

**解决方案：**
```bash
pip install Pillow
```

### Q: 无法访问API文档

**解决方案：**
1. 确保服务器正在运行
2. 检查防火墙设置
3. 访问 http://127.0.0.1:8000/api/docs

### Q: JWT令牌过期

**解决方案：**
使用refresh_token获取新的access_token：

```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

## 开发建议

### 1. 启用调试工具

安装Django Debug Toolbar（可选）：

```bash
pip install django-debug-toolbar
```

### 2. 配置日志级别

修改 `config/settings.py` 中的日志配置，将级别设为 DEBUG：

```python
'root': {
    'handlers': ['console', 'file'],
    'level': 'DEBUG',  # 开发环境使用DEBUG
}
```

### 3. 使用虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

## 下一步

1. 阅读 `REFACTORING_SUMMARY.md` 了解系统架构
2. 阅读 `MIGRATION_GUIDE.md` 了解数据迁移详情
3. 访问 `/api/docs` 查看完整API文档
4. 开始开发您的功能！

## 获取帮助

- 查看项目README.md
- 查看API文档：http://localhost:8000/api/docs
- 检查日志文件：`logs/django.log`
