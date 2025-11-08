"""
自定义过滤器 - 用于管理后台筛选功能
"""
from django.contrib import admin
from django.db import models
from django.utils import timezone
from datetime import timedelta


class UserFilter(admin.SimpleListFilter):
    """按用户筛选（增强版）"""
    title = '用户筛选'
    parameter_name = 'user_filter'
    
    def lookups(self, request, model_admin):
        # 获取有评估记录的用户，按活跃度排序
        from apps.scales.models import ScaleResult
        from apps.users.models import User
        
        user_ids = ScaleResult.objects.values_list('user_id', flat=True).distinct()
        user_activity = ScaleResult.objects.filter(user_id__in=user_ids).values('user_id').annotate(
            count=models.Count('id'),
            latest=models.Max('created_at')
        ).order_by('-latest')[:50]
        
        users = []
        for activity in user_activity:
            user_id = activity['user_id']
            try:
                user = User.objects.get(id=user_id)
                display_name = f"{user.real_name or '匿名用户'} ({user.age}岁)" if user.real_name else f"用户{str(user_id)[:8]}"
                activity_info = f" ({activity['count']}次评估)"
                users.append((str(user_id), display_name + activity_info))
            except User.DoesNotExist:
                users.append((str(user_id), f"用户{str(user_id)[:8]} ({activity['count']}次评估)"))
        return users
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user_id=self.value())
        return queryset


class ScaleFilter(admin.SimpleListFilter):
    """按量表筛选（增强版）"""
    title = '量表筛选'
    parameter_name = 'scale_filter'
    
    def lookups(self, request, model_admin):
        # 获取有记录的量表，按使用频率排序
        from apps.scales.models import ScaleConfig
        
        scales = ScaleConfig.objects.filter(
            results__isnull=False
        ).annotate(
            usage_count=models.Count('results')
        ).order_by('-usage_count')[:30]
        
        return [(str(scale.id), f"{scale.name} ({scale.code}) - {scale.usage_count}次使用") for scale in scales]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(scale_config_id=self.value())
        return queryset


class StatusFilter(admin.SimpleListFilter):
    """按状态筛选（增强版）"""
    title = '状态筛选'
    parameter_name = 'status_detail'
    
    def lookups(self, request, model_admin):
        return [
            ('active_normal', '启用-正常结果'),
            ('active_abnormal', '启用-异常结果'),
            ('draft', '草稿'),
            ('recent_completed', '最近完成（7天内）'),
            ('long_duration', '答题时间较长（>10分钟）'),
        ]
    
    def queryset(self, request, queryset):
        if self.value() == 'active_normal':
            return queryset.filter(scale_config__status='active').filter(
                models.Q(analysis__is_abnormal=False) | models.Q(analysis__is_abnormal__isnull=True)
            )
        elif self.value() == 'active_abnormal':
            return queryset.filter(scale_config__status='active', analysis__is_abnormal=True)
        elif self.value() == 'draft':
            return queryset.filter(scale_config__status='draft')
        elif self.value() == 'recent_completed':
            return queryset.filter(completed_at__gte=timezone.now() - timedelta(days=7))
        elif self.value() == 'long_duration':
            return queryset.filter(duration_ms__gt=600000)  # 10分钟
        return queryset


class AssessmentStatusFilter(admin.SimpleListFilter):
    """智能测评状态筛选"""
    title = '测评状态'
    parameter_name = 'assessment_status'
    
    def lookups(self, request, model_admin):
        return [
            ('in_progress_recent', '最近进行（24小时内）'),
            ('completed_today', '今日完成'),
            ('abandoned_recent', '最近放弃（3天内）'),
            ('high_risk', '高风险结果'),
            ('long_duration', '耗时较长（>30分钟）'),
        ]
    
    def queryset(self, request, queryset):
        if self.value() == 'in_progress_recent':
            return queryset.filter(status='in_progress', started_at__gte=timezone.now() - timedelta(hours=24))
        elif self.value() == 'completed_today':
            return queryset.filter(status='completed', completed_at__gte=timezone.now() - timedelta(days=1))
        elif self.value() == 'abandoned_recent':
            return queryset.filter(status='abandoned', updated_at__gte=timezone.now() - timedelta(days=3))
        elif self.value() == 'high_risk':
            return queryset.filter(
                status='completed',
                final_result__risk_level='高风险'
            )
        elif self.value() == 'long_duration':
            return queryset.annotate(
                duration=models.F('completed_at') - models.F('started_at')
            ).filter(duration__gt=timedelta(minutes=30))
        return queryset