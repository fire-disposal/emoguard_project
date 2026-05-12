"""
已弃用 — Celery Beat 已替换为轻量级调度器 run_scheduler
保留此文件以避免历史调用出错
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "（已弃用）创建定时任务，现由 run_scheduler 替代"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE(
            "ℹ️ setup_periodic_tasks 已弃用，定时任务现在由 run_scheduler 管理。"
        ))
