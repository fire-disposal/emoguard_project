"""
Django 管理命令：创建定时任务
用于在部署时自动创建 Celery Beat 定时任务
"""
from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from django.utils import timezone
import json

class Command(BaseCommand):
    help = '创建情绪测评提醒定时任务'

    def handle(self, *args, **options):
        # 创建早上 9:00 的定时任务
        morning_schedule, created = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='9',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
            timezone=timezone.get_current_timezone()
        )
        
        morning_task, created = PeriodicTask.objects.get_or_create(
            crontab=morning_schedule,
            name='早上情绪测评提醒',
            task='apps.notice.tasks.send_morning_reminder',
            defaults={
                'enabled': True,
                'description': '每天早上 9:00 提醒用户进行早间情绪测评',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✅ 早上情绪测评提醒任务已创建'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ 早上情绪测评提醒任务已存在'))

        # 创建晚上 21:00 的定时任务
        evening_schedule, created = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='21',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
            timezone=timezone.get_current_timezone()
        )
        
        evening_task, created = PeriodicTask.objects.get_or_create(
            crontab=evening_schedule,
            name='晚上情绪测评提醒',
            task='apps.notice.tasks.send_evening_reminder',
            defaults={
                'enabled': True,
                'description': '每天晚上 21:00 提醒用户进行晚间情绪测评',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✅ 晚上情绪测评提醒任务已创建'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ 晚上情绪测评提醒任务已存在'))

        self.stdout.write(self.style.SUCCESS('🎉 定时任务设置完成！'))