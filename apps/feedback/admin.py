"""用户反馈管理后台 - 支持人口学信息导出"""
from django.contrib import admin
from import_export.admin import ExportActionModelAdmin
from import_export import resources, fields
from apps.feedback.models import Feedback
from apps.users.demographic_export import build_excel_with_demographics, build_csv_with_demographics

class FeedbackResource(resources.ModelResource):
    """用户反馈导出资源（人口学信息由导出模块统一处理）"""
    id = fields.Field(column_name="反馈ID", attribute="id")
    user_id_display = fields.Field(column_name="用户ID", attribute="user_id")
    rating = fields.Field(column_name="评分", attribute="rating")
    content = fields.Field(column_name="反馈内容", attribute="content")
    is_processed = fields.Field(column_name="已处理", attribute="is_processed")
    created_at = fields.Field(column_name="创建时间", attribute="created_at")

    class Meta:
        model = Feedback
        fields = [
            "id", "user_id_display", "rating", "content", "is_processed", "created_at"
        ]
        export_order = fields
        skip_unchanged = True

@admin.register(Feedback)
class FeedbackAdmin(ExportActionModelAdmin):
    resource_class = FeedbackResource
    list_display = ['id', 'user', 'rating', 'content', 'created_at', 'is_processed']
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

    def export_selected_excel(self, request, queryset):
        """导出反馈为Excel格式（调用人口学信息导出工具）"""
        extra_field_order = [
            "id", "rating", "content", "is_processed", "created_at"
        ]
        extra_field_titles = [
            "反馈ID", "评分", "反馈内容", "已处理", "创建时间"
        ]
        def get_user_id(record):
            return record.user_id if hasattr(record, "user_id") else None
        return build_excel_with_demographics(queryset, get_user_id, extra_field_order, extra_field_titles)
    export_selected_excel.short_description = "导出为Excel"

    def export_selected_csv(self, request, queryset):
        """导出反馈为CSV格式（调用人口学信息导出工具）"""
        extra_field_order = [
            "id", "rating", "content", "is_processed", "created_at"
        ]
        extra_field_titles = [
            "反馈ID", "评分", "反馈内容", "已处理", "创建时间"
        ]
        def get_user_id(record):
            return record.user_id if hasattr(record, "user_id") else None
        return build_csv_with_demographics(queryset, get_user_id, extra_field_order, extra_field_titles)
    export_selected_csv.short_description = "导出为CSV"