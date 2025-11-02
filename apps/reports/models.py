from django.db import models

class HealthReport(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.UUIDField(verbose_name='用户', db_index=True)
    assessment_id = models.IntegerField(verbose_name='评估ID')
    report_type = models.CharField(max_length=50, verbose_name='报告类型')
    overall_risk = models.CharField(max_length=50, verbose_name='总体风险')
    summary = models.TextField(verbose_name='摘要')
    recommendations = models.JSONField(verbose_name='建议', default=list)
    professional_advice = models.TextField(verbose_name='专业建议')
    trend_analysis = models.TextField(verbose_name='趋势分析')
    trend_data = models.JSONField(verbose_name='趋势数据', default=dict)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '健康报告'
        verbose_name_plural = '健康报告'
        ordering = ['-created_at']

    def __str__(self):
        return f"健康报告({self.id}) - 用户: {self.user_id}"