from django.db import models
from django.conf import settings


class UserQuota(models.Model):
    """
    订阅额度表：记录用户对某个模板ID还有多少次接收机会
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notice_quotas'
    )
    template_id = models.CharField("微信模板ID", max_length=64)
    count = models.PositiveIntegerField("剩余次数", default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # 联合唯一索引：一个用户对同一个模板只有一条记录
        unique_together = ('user', 'template_id')
        verbose_name = "用户订阅额度"
        verbose_name_plural = "用户订阅额度"

    def __str__(self):
        return f"{self.user.username} - {self.template_id}: {self.count}"


class NotificationLog(models.Model):
    STATUS_CHOICES = (
        ('pending', '等待发送'),
        ('success', '发送成功'),
        ('failed', '发送失败'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    template_id = models.CharField("模板ID", max_length=64)
    
    # 存储发送的具体参数，如 {'thing1': '心理测评', 'time2': '2023-11-01'}
    message_data = models.JSONField("消息内容") 
    
    # 业务关联字段（可选）：方便查询是针对哪次测评发的
    assessment_id = models.IntegerField(null=True, blank=True) 
    
    status = models.CharField(choices=STATUS_CHOICES, default='pending', max_length=20)
    wechat_msg_id = models.CharField("微信返回的MsgID", max_length=64, blank=True, null=True)
    error_response = models.TextField("错误信息", blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True) # 创建任务时间
    sent_at = models.DateTimeField(null=True, blank=True) # 实际发送时间

    class Meta:
        verbose_name = "通知发送日志"
        verbose_name_plural = "通知发送日志"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.template_id}: {self.status}"