from django.db import models

class ScaleResult(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.UUIDField()
    scale_code = models.CharField(max_length=64, verbose_name="量表代码", default="unknown")
    score = models.FloatField(default=0.0, verbose_name="分数")
    selected_options = models.JSONField(default=list, verbose_name="选项选择")
    conclusion = models.TextField(blank=True, verbose_name="结论摘要")
    started_at = models.DateTimeField(verbose_name="开始时间")
    completed_at = models.DateTimeField(verbose_name="完成时间")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result-{self.id} 用户:{self.user_id} 量表:{self.scale_code}"

    class Meta:
        verbose_name = "量表结果"
        verbose_name_plural = "量表结果"
        indexes = [
            models.Index(fields=['user_id', '-created_at'])
        ]