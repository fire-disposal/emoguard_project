from django.db import models
from apps.users.models import User


class MoodJournal(models.Model):
    """情绪日记模型 - 精简设计"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="mood_journals",
        verbose_name="用户",
    )
    mainMood = models.CharField(
        max_length=32, verbose_name="主观情绪", blank=True, null=True
    )
    moodIntensity = models.IntegerField(verbose_name="情绪强度", blank=True, null=True)
    mainMoodOther = models.CharField(
        max_length=64, verbose_name="其他情绪文本", blank=True, null=True
    )
    moodSupplementTags = models.JSONField(
        verbose_name="情绪补充标签", blank=True, null=True
    )
    moodSupplementText = models.CharField(
        max_length=128, verbose_name="情绪补充说明", blank=True, null=True
    )
    record_date = models.DateTimeField(verbose_name="记录日期", auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "情绪日记"
        verbose_name_plural = "情绪日记"
        ordering = ["-record_date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "-record_date"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.user.display_name} - {self.mainMood} - 强度{self.moodIntensity} - {self.record_date.strftime('%Y-%m-%d')}"
