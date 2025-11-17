"""用户反馈模型 - 简化版本"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Feedback(models.Model):
    """用户反馈模型 - 支持评分和文本反馈（简化版）"""
    
    # 使用自增ID（更简洁）
    id = models.AutoField(primary_key=True)
    
    # 关联用户（可以为空，允许匿名反馈）
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='用户',
        help_text='提交反馈的用户，可为空表示匿名反馈'
    )
    
    # 评分（1-5星制，更直观）
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='评分',
        help_text='1-5星评分，5星为最高分'
    )
    
    # 文本反馈（可选，最多500字）
    content = models.TextField(
        max_length=500,
        blank=True,
        default='',
        verbose_name='反馈内容',
        help_text='可选的文本反馈，最多500字'
    )
    
    # 创建时间（自动记录）
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    # 处理状态
    is_processed = models.BooleanField(
        default=False,
        verbose_name='已处理'
    )
    
    class Meta:
        verbose_name = '用户反馈'
        verbose_name_plural = '用户反馈'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['rating']),
            models.Index(fields=['is_processed']),
        ]
    
    def __str__(self):
        if self.user:
            return f"{self.user.display_name} 的反馈 - {self.rating}星"
        return f"匿名用户反馈 - {self.rating}星"