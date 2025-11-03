from django.db import models

class ScaleConfig(models.Model):
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('active', '启用'),
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=64, unique=True)
    version = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=64)
    questions = models.JSONField(default=list)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = "量表配置"
        verbose_name_plural = "量表配置"

class ScaleResult(models.Model):
    STATUS_CHOICES = (
        ('completed', '已完成'),
    )
    id = models.AutoField(primary_key=True)
    user_id = models.UUIDField()
    scale_config = models.ForeignKey(ScaleConfig, on_delete=models.CASCADE, related_name='results')
    selected_options = models.JSONField(default=list)
    duration_ms = models.IntegerField()
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='completed')
    analysis = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Result-{self.id} 用户:{self.user_id}"

    class Meta:
        verbose_name = "量表结果"
        verbose_name_plural = "量表结果"