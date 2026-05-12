"""
轻量级进程内调度器 — 替代 Celery Beat
每 30 秒检查一次，到点执行 send_mood_reminder
"""
import time
import signal
import sys
from datetime import datetime
from django.core.management.base import BaseCommand
from apps.notice.tasks import send_mood_reminder


class Command(BaseCommand):
    help = "轻量级进程内调度器，替代 Celery Beat"

    def add_arguments(self, parser):
        parser.add_argument(
            "--oneshot",
            action="store_true",
            help="执行一次后退出（用于 cron 模式）",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🕐 轻量调度器启动 (9:00 早间 / 21:00 晚间)"))

        if options["oneshot"]:
            self._check_and_run()
            return

        # 优雅退出
        shutdown = False

        def _handler(signum, frame):
            nonlocal shutdown
            shutdown = True
            self.stdout.write(self.style.WARNING("收到退出信号，调度器关闭..."))

        signal.signal(signal.SIGTERM, _handler)
        signal.signal(signal.SIGINT, _handler)

        last_run = {"morning": None, "evening": None}

        while not shutdown:
            try:
                now = datetime.now()
                today = now.strftime("%Y%m%d")

                if now.hour == 9 and now.minute == 0 and last_run["morning"] != today:
                    self.stdout.write(f"[{now}] 执行早间提醒...")
                    send_mood_reminder(period="morning")
                    last_run["morning"] = today

                if now.hour == 21 and now.minute == 0 and last_run["evening"] != today:
                    self.stdout.write(f"[{now}] 执行晚间提醒...")
                    send_mood_reminder(period="evening")
                    last_run["evening"] = today

                time.sleep(30)
            except Exception as e:
                self.stderr.write(f"调度器异常: {e}")
                time.sleep(30)

        self.stdout.write("调度器已退出.")
