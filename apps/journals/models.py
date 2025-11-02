from django.db import models
from apps.users.models import User

class MoodJournal(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mood_journals')
    mood_score = models.PositiveSmallIntegerField(verbose_name='情绪分数', help_text='1-10', default=5)
    mood_name = models.CharField(max_length=16, verbose_name='情绪名称')
    mood_emoji = models.CharField(max_length=8, verbose_name='情绪表情')
    text = models.CharField(max_length=512, verbose_name='日记内容')
    record_date = models.DateTimeField(verbose_name='记录日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '情绪日记'
        verbose_name_plural = '情绪日记'
        ordering = ['-record_date', '-created_at']

    def __str__(self):
        return f"{self.user} {self.mood_name} {self.record_date.strftime('%Y-%m-%d')}"