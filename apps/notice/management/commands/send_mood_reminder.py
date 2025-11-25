from django.core.management.base import BaseCommand, CommandError
from apps.notice.tasks import send_mood_reminder

class Command(BaseCommand):
    help = "立即推送情绪测评提醒（period: morning/evening）"

    def add_arguments(self, parser):
        parser.add_argument(
            "--period",
            type=str,
            choices=["morning", "evening"],
            default="morning",
            help="推送类型：morning 或 evening"
        )

    def handle(self, *args, **options):
        period = options["period"]
        self.stdout.write(self.style.NOTICE(f"开始推送 {period} 测评提醒..."))
        try:
            send_mood_reminder(period=period)
            self.stdout.write(self.style.SUCCESS(f"{period} 测评提醒推送任务已执行"))
        except Exception as e:
            raise CommandError(f"推送失败: {e}")