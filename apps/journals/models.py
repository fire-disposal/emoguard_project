from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.users.models import User


class MoodJournal(models.Model):
    """情绪日记模型 - 精简设计"""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mood_journals', verbose_name='用户')
    mood_score = models.PositiveSmallIntegerField(
        verbose_name='情绪分数',
        help_text='1-10分',
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5
    )
    mood_name = models.CharField(
        max_length=32,
        verbose_name='情绪名称',
        help_text='如开心、难过等',
        default=''
    )
    text = models.TextField(
        max_length=1000,
        blank=True,
        default='',
        verbose_name='日记内容',
        help_text='用户自评内容，最多1000字'
    )
    record_date = models.DateTimeField(verbose_name='记录日期', auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '情绪日记'
        verbose_name_plural = '情绪日记'
        ordering = ['-record_date', '-created_at']
        indexes = [
            models.Index(fields=['user', '-record_date']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.user.display_name} - {self.mood_name} - 分数{self.mood_score} - {self.record_date.strftime('%Y-%m-%d')}"