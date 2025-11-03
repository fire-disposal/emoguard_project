# 认知照顾情绪监测系统后端

基于Django + Django-Ninja构建的情绪健康监测平台后端API服务。

## 功能特性

### 核心模块
- **用户与权限管理**: 支持微信OpenID/UnionID登录，角色权限控制
- **文章资讯**: 内容管理系统，支持草稿/发布状态管理
- **情绪日记**: 用户情绪记录与趋势分析
- **健康报告**: 生成个性化健康评估报告
- **量表评估**: 心理健康量表配置与评估
- **微信小程序授权**: 完整的微信登录授权流程

### 技术特性
- RESTful API设计
- JWT认证授权
- 数据分页与过滤
- 时区本地化支持
- 完善的错误处理
- 日志记录系统

## 技术栈

- **框架**: Django 5.2.7 + Django-Ninja
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **认证**: JWT + 微信小程序授权
- **部署**: Gunicorn + Nginx
- **监控**: Sentry日志监控

## 快速开始

### 环境要求
- Python 3.11+
- pip包管理器

### 安装依赖
```bash
pip install -r requirements.txt
```

### 数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```

### 创建超级用户
```bash
python manage.py createsuperuser
```

### 量表初始化（导入yaml量表配置）
```bash
python manage.py load_scales_from_yaml
```

### 运行开发服务器
```bash
python manage.py runserver
```

### 访问API文档
启动服务器后访问: http://localhost:8000/api/docs

## API端点

### 用户认证
- `POST /api/users/wechat/login` - 微信登录
- `GET /api/users/me` - 获取当前用户信息
- `POST /api/token/pair/` - 获取令牌对（访问令牌+刷新令牌）- django-ninja-jwt提供
- `POST /api/token/refresh/` - 刷新访问令牌 - django-ninja-jwt提供
- `POST /api/token/verify/` - 验证令牌 - django-ninja-jwt提供

### 用户资料
- `GET /api/users/profiles` - 获取用户资料列表
- `POST /api/users/profiles` - 创建用户资料
- `PUT /api/users/profiles/{id}` - 更新用户资料

### 文章资讯
- `GET /api/articles/` - 获取文章列表
- `POST /api/articles/` - 创建文章
- `GET /api/articles/{id}` - 获取文章详情
- `PUT /api/articles/{id}` - 更新文章
- `DELETE /api/articles/{id}` - 删除文章
- `POST /api/articles/{id}/publish` - 发布文章

### 情绪日记
- `GET /api/journals/` - 获取情绪日记列表
- `POST /api/journals/` - 创建情绪日记
- `GET /api/journals/{id}` - 获取日记详情
- `PUT /api/journals/{id}` - 更新日记
- `DELETE /api/journals/{id}` - 删除日记
- `GET /api/journals/statistics/daily` - 获取日情绪统计
- `GET /api/journals/trends/score` - 获取情绪分数趋势

### 健康报告
- `GET /api/reports/` - 获取健康报告列表
- `POST /api/reports/` - 创建健康报告
- `GET /api/reports/{id}` - 获取报告详情
- `PUT /api/reports/{id}` - 更新报告
- `DELETE /api/reports/{id}` - 删除报告
- `GET /api/reports/summary/{user_id}` - 获取用户报告摘要
- `GET /api/reports/trends/{user_id}` - 获取健康趋势

### 量表评估
- `GET /api/scales/configs` - 获取量表配置列表
- `POST /api/scales/configs` - 创建量表配置
- `GET /api/scales/configs/{id}` - 获取量表配置详情
- `PUT /api/scales/configs/{id}` - 更新量表配置
- `GET /api/scales/results` - 获取量表结果列表
- `POST /api/scales/results` - 创建量表结果
- `POST /api/scales/results/{id}/analyze` - 分析量表结果
- `GET /api/scales/completion-stats` - 获取完成统计

## 配置说明

### 微信小程序配置
在 `config/settings.py` 中配置：
```python
WECHAT_MINI_PROGRAM_APP_ID = "你的小程序AppID"
WECHAT_MINI_PROGRAM_APP_SECRET = "你的小程序AppSecret"
```

### 数据库配置
生产环境建议使用PostgreSQL：
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_database_name',
        'USER': 'your_database_user',
        'PASSWORD': 'your_database_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### JWT配置 (Django Ninja JWT)
```python
NINJA_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('ninja_jwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'users.User',  # 指定用户模型
}
```

### 标准JWT使用示例
```bash
# 获取令牌对
curl -X POST -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}' \
  http://localhost:8000/api/token/pair/

# 使用访问令牌访问受保护资源
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/users/me/

# 刷新访问令牌
curl -X POST -H "Content-Type: application/json" \
  -d '{"refresh":"YOUR_REFRESH_TOKEN"}' \
  http://localhost:8000/api/token/refresh/
```

## 部署指南

### 生产环境部署
1. 配置环境变量
2. 设置静态文件服务
3. 配置数据库连接
4. 设置反向代理（Nginx）
5. 配置HTTPS
6. 设置进程管理（Supervisor）

### Docker部署
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 开发规范

### 代码风格
- 遵循PEP 8规范
- 使用Black进行代码格式化
- 使用isort进行导入排序

### API设计
- 使用RESTful设计原则
- 统一的响应格式
- 完善的错误处理
- 详细的API文档

### 数据库设计
- 使用有意义的字段名
- 添加适当的索引
- 保持数据完整性

## 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交代码变更
4. 创建Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交Issue或联系维护者。