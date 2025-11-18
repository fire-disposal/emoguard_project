from django.db import models

class CognitiveAssessmentRecord(models.Model):
    """
    认知测评答卷记录（无流程控制，仅存储答卷与评分结果）
    """
    id = models.AutoField(primary_key=True)
    user_id = models.UUIDField(verbose_name='用户ID', db_index=True)
    # 用户信息字段拷贝
    real_name = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='真实姓名'
    )
    
    gender = models.CharField(
        max_length=10,
        blank=True,
        default='',
        verbose_name='性别'
    )
    
    age = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='年龄'
    )
    
    education = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name='学历'
    )
    
    province = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='所在省份'
    )
    city = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='所在城市'
    )
    district = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='所在区县'
    )

    phone = models.CharField(
        max_length=11,
        blank=True,
        null=True,
    )

    # 预留所有常见量表的得分字段，均允许为空
    score_scd = models.FloatField(verbose_name='SCD得分', null=True, blank=True)
    score_mmse = models.FloatField(verbose_name='MMSE得分', null=True, blank=True)
    score_moca = models.FloatField(verbose_name='MoCA得分', null=True, blank=True)
    score_gad7 = models.FloatField(verbose_name='GAD7得分', null=True, blank=True)
    score_phq9 = models.FloatField(verbose_name='PHQ9得分', null=True, blank=True)
    score_adl = models.FloatField(verbose_name='ADL得分', null=True, blank=True)
    score_sus = models.FloatField(verbose_name='SUS得分', null=True, blank=True)
    analysis = models.JSONField(default=dict, blank=True, verbose_name='评分分析')
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = "认知测评答卷"
        verbose_name_plural = "认知测评答卷"
        indexes = [
            models.Index(fields=['user_id', 'province']),
        ]