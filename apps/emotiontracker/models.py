from django.db import models
from django.utils import timezone

class EmotionRecord(models.Model):
    # 定义常量，防止硬编码
    PERIOD_MORNING = 'morning'
    PERIOD_EVENING = 'evening'
    PERIOD_CHOICES = (
        (PERIOD_MORNING, '早晨'),
        (PERIOD_EVENING, '晚间'),
    )

    id = models.AutoField(primary_key=True)
    user_id = models.UUIDField(verbose_name='用户', db_index=True)
    
    # 新增：明确的记录日期（不含时分秒），用于定位“今天”
    record_date = models.DateField(verbose_name='记录日期', default=timezone.now) 
    
    # 修改：规范化 period 字段
    period = models.CharField(max_length=16, verbose_name='测评时间段', choices=PERIOD_CHOICES,null=True)

    # ... 其他字段保持不变 ...
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

    class Meta:
        verbose_name = '情绪测试'
        verbose_name_plural = '情绪测试EMA'
        ordering = ['-created_at']
        # 核心修改：添加联合唯一约束
        # 这保证了：同一个用户，在同一天，同一个时段，只能有一条记录
        constraints = [
            models.UniqueConstraint(
                fields=['user_id', 'record_date', 'period'], 
                name='unique_user_date_period'
            )
        ]

    def __str__(self):
        return f"{self.user_id} - {self.record_date} ({self.period})"