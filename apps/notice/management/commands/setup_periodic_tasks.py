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

        def upsert(name, hour, kwargs, description):
            schedule, _ = CrontabSchedule.objects.get_or_create(
                minute="0", hour=str(hour), day_of_week="*",
                day_of_month="*", month_of_year="*", timezone=tz,
            )
            task, created = PeriodicTask.objects.update_or_create(
                name=name,
                defaults={
                    "crontab": schedule,
                    "task": "apps.notice.tasks.send_mood_reminder",
                    "kwargs": json.dumps(kwargs),
                    "enabled": True,
                    "description": description,
                },
            )
            verb = "已创建" if created else "已更新"
            self.stdout.write(self.style.SUCCESS(f"✅ {name} 定时任务{verb}"))

        upsert("早上情绪测评提醒", 9, {"period": "morning"}, "每天早上 9:00 提醒用户进行早间情绪测评")
        upsert("晚上情绪测评提醒", 21, {"period": "evening"}, "每天晚上 21:00 提醒用户进行晚间情绪测评")
        self.stdout.write(self.style.SUCCESS("🎉 定时任务设置完成！"))