"""
Celery 配置
"""
import os
from celery import Celery
from django.conf import settings

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 创建 Celery 实例
app = Celery('emoguard')

# 使用 Django 配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务
app.autodiscover_tasks()

# 配置时区
app.conf.timezone = settings.TIME_ZONE

# 配置任务路由
app.conf.task_routes = {
    'apps.notice.tasks.send_mood_reminder': {'queue': 'notice'}
}
