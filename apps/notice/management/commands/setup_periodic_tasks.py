"""
Django 管理命令：创建情绪测评提醒定时任务
用于在部署时自动创建 Celery Beat 定时任务
"""
from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from django.utils import timezone
import json


class Command(BaseCommand):
    help = "创建情绪测评提醒定时任务（早上 9:00 / 晚上 21:00）"

    def handle(self, *args, **options):
        tz = timezone.get_current_timezone()

        # ---------------- 早上 9:00 ----------------
        morning_schedule, _ = CrontabSchedule.objects.get_or_create(
            minute="0",
            hour="9",
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
            timezone=tz,
        )

        morning_task, created = PeriodicTask.objects.get_or_create(
            crontab=morning_schedule,
            name="早上情绪测评提醒",
            defaults={
                "task": "apps.notice.tasks.send_mood_reminder",
                "kwargs": json.dumps({"period": "morning"}),
                "enabled": True,
                "description": "每天早上 9:00 提醒用户进行早间情绪测评",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("✅ 早上情绪测评提醒任务已创建"))
        else:
            # 若已存在，确保字段是最新的
            updated = False
            if morning_task.task != "apps.notice.tasks.send_mood_reminder":
                morning_task.task = "apps.notice.tasks.send_mood_reminder"
                updated = True
            if morning_task.kwargs != json.dumps({"period": "morning"}):
                morning_task.kwargs = json.dumps({"period": "morning"})
                updated = True
            if updated:
                morning_task.save()
                self.stdout.write(self.style.WARNING("⚠️ 早上任务已存在，已更新字段"))
            else:
                self.stdout.write(self.style.WARNING("⚠️ 早上情绪测评提醒任务已存在"))

        # ---------------- 晚上 21:00 ----------------
        evening_schedule, _ = CrontabSchedule.objects.get_or_create(
            minute="0",
            hour="21",
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
            timezone=tz,
        )

        evening_task, created = PeriodicTask.objects.get_or_create(
            crontab=evening_schedule,
            name="晚上情绪测评提醒",
            defaults={
                "task": "apps.notice.tasks.send_mood_reminder",
                "kwargs": json.dumps({"period": "evening"}),
                "enabled": True,
                "description": "每天晚上 21:00 提醒用户进行晚间情绪测评",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("✅ 晚上情绪测评提醒任务已创建"))
        else:
            updated = False
            if evening_task.task != "apps.notice.tasks.send_mood_reminder":
                evening_task.task = "apps.notice.tasks.send_mood_reminder"
                updated = True
            if evening_task.kwargs != json.dumps({"period": "evening"}):
                evening_task.kwargs = json.dumps({"period": "evening"})
                updated = True
            if updated:
                evening_task.save()
                self.stdout.write(self.style.WARNING("⚠️ 晚上任务已存在，已更新字段"))
            else:
                self.stdout.write(self.style.WARNING("⚠️ 晚上情绪测评提醒任务已存在"))

        self.stdout.write(self.style.SUCCESS("🎉 定时任务设置完成！"))