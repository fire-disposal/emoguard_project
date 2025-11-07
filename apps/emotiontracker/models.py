from django.db import models

class EmotionRecord(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.UUIDField(verbose_name='用户', db_index=True)
    depression = models.IntegerField(verbose_name='抑郁分数')
    anxiety = models.IntegerField(verbose_name='焦虑分数')
    energy = models.IntegerField(verbose_name='精力分数')
    sleep = models.IntegerField(verbose_name='睡眠分数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='记录时间')

    class Meta:
        verbose_name = '情绪四维度记录'
        verbose_name_plural = '情绪四维度记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"EmotionRecord({self.id}) - 用户: {self.user_id}"