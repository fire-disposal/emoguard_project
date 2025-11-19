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
    'apps.notice.tasks.send_morning_reminder': {'queue': 'notice'},
    'apps.notice.tasks.send_evening_reminder': {'queue': 'notice'},
}

# 配置定时任务（需要在 Django admin 中通过 django-celery-beat 管理）
app.conf.beat_schedule = {
    'send-morning-reminder': {
        'task': 'apps.notice.tasks.send_morning_reminder',
        'schedule': '0 9 * * *',  # 每天早上 9:00
    },
    'send-evening-reminder': {
        'task': 'apps.notice.tasks.send_evening_reminder',
        'schedule': '0 21 * * *',  # 每天晚上 21:00
    },
}