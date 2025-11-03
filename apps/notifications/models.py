"""
通知系统模型
"""
from django.db import models
from apps.users.models import User


class Notification(models.Model):
    """
    通知模型
    支持系统消息、评估通知、提醒通知等
    """
    
    TYPE_CHOICES = [
        ('system', '系统通知'),
        ('assessment', '评估通知'),
        ('reminder', '提醒通知'),
    ]
    
    id = models.AutoField(primary_key=True, verbose_name='通知ID')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='接收用户'
    )
    title = models.CharField(max_length=100, verbose_name='通知标题')
    content = models.TextField(verbose_name='通知内容')
    notification_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='system',
        verbose_name='通知类型'
    )
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    
    # 关联对象（可选）
    related_id = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='关联对象ID',
        help_text='关联的评估、报告等对象的ID'
    )
    related_type = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='关联对象类型',
        help_text='如: scale_result, health_report等'
    )
    
    # 时间字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    read_at = models.DateTimeField(blank=True, null=True, verbose_name='阅读时间')
    
    class Meta:
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.display_name} - {self.title}"
    
    def mark_as_read(self):
        """标记为已读"""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
