"""用户反馈管理后台 - 支持人口学信息导出"""
from django.contrib import admin
from import_export.admin import ExportActionModelAdmin
from import_export import resources, fields
from apps.feedback.models import Feedback
from apps.users.admin_mixins import BaseAdminMixin


class FeedbackResource(resources.ModelResource):
    """用户反馈导出资源（人口学信息由导出模块统一处理）"""
    id = fields.Field(column_name="反馈ID", attribute="id")
    user_id_display = fields.Field(column_name="用户ID", attribute="user_id")
    rating = fields.Field(column_name="评分", attribute="rating")
    content = fields.Field(column_name="反馈内容", attribute="content")
    is_processed = fields.Field(column_name="已处理", attribute="is_processed")
    created_at = fields.Field(column_name="创建时间", attribute="created_at")

    def dehydrate_created_at(self, obj):
        if obj.created_at:
            return obj.created_at.strftime("%Y年%m月%d日 %H点%M分%S秒")
        return ""

    class Meta:
        model = Feedback
        fields = [
            "id", "user_id_display", "rating", "content", "is_processed", "created_at"
        ]
        export_order = fields
        skip_unchanged = True


@admin.register(Feedback)
class FeedbackAdmin(BaseAdminMixin, ExportActionModelAdmin):
    resource_class = FeedbackResource
    
    # 定义导出字段配置
    export_extra_fields = [
        "id", "rating", "content", "is_processed", "created_at"
    ]
    export_extra_titles = [
        "反馈ID", "评分", "反馈内容", "已处理", "创建时间"
    ]
    
    list_display = ['id', 'user_info', 'rating', 'content', 'created_at', 'is_processed']  # 使用统一的user_info
    list_filter = ['rating', 'is_processed', 'created_at']
    search_fields = ['content', 'user__display_name', 'user__phone']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'rating', 'content')
        }),
        ('处理状态', {
            'fields': ('is_processed',)
        }),
        ('时间信息', {
            'fields': ('created_at',)
        }),
    )
    
    actions = ["export_selected_excel", "export_selected_csv"]