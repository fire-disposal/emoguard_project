from django.db import models
from django.utils import timezone

class EmotionRecord(models.Model):
    PERIOD_MORNING = 'morning'
    PERIOD_EVENING = 'evening'
    PERIOD_CHOICES = (
        (PERIOD_MORNING, '早晨'),
        (PERIOD_EVENING, '晚间'),
    )
    id = models.AutoField(primary_key=True)
    user_id = models.UUIDField(verbose_name='用户', db_index=True)
    record_date = models.DateField(verbose_name='记录日期', default=timezone.now) 
    period = models.CharField(max_length=16, verbose_name='测评时间段', choices=PERIOD_CHOICES,null=True)
    depression = models.IntegerField(verbose_name='抑郁分数')
    anxiety = models.IntegerField(verbose_name='焦虑分数')
    energy = models.IntegerField(verbose_name='精力分数')
    sleep = models.IntegerField(verbose_name='睡眠分数')
    mainMood = models.CharField(max_length=32, verbose_name='主观情绪', blank=True, null=True)
    moodIntensity = models.IntegerField(verbose_name='情绪强度', blank=True, null=True)
    mainMoodOther = models.CharField(max_length=64, verbose_name='其他情绪文本', blank=True, null=True)
    moodSupplementTags = models.JSONField(verbose_name='情绪补充标签', blank=True, null=True)
    moodSupplementText = models.CharField(max_length=128, verbose_name='情绪补充说明', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='记录时间') # 仅作创建时间审计
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='开始作答时间')

    class Meta:
        verbose_name = '情绪测试'
        verbose_name_plural = '情绪测试EMA'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user_id', 'record_date', 'period'], 
                name='unique_user_date_period'
            )
        ]

    def __str__(self):
        return f"{self.user_id} - {self.record_date} ({self.period})"