# 使用uv官方镜像作为基础镜像
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_NO_CACHE=1 \
    UV_COMPILE_BYTECODE=1 \
    PORT=8000

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY pyproject.toml uv.lock ./

# 使用uv sync安装依赖
RUN uv sync --frozen 

# 复制入口脚本
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# 复制项目代码
COPY . .

# 创建必要的目录
RUN mkdir -p media logs staticfiles

# 设置文件权限
RUN chmod -R 755 /app/media /app/logs /app/staticfiles

# 收集静态文件
RUN .venv/bin/python manage.py collectstatic --noinput

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD .venv/bin/python -c "import requests; requests.get('http://localhost:8000/health/', timeout=10)" || exit 1

# 使用非root用户运行（安全最佳实践）
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 启动命令 - 使用入口脚本处理初始化，然后启动gunicorn
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD [".venv/bin/gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--keep-alive", "5", "--max-requests", "1000", "--max-requests-jitter", "100", "config.wsgi:application"]