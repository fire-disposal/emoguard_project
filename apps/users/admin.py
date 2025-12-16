"""用户管理 admin 配置"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.contrib.auth.models import Group
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户管理"""

    # 列表显示字段，将 is_tracked 放在显眼位置
    list_display = [
        "real_name",
        "gender",
        "age",
        "education",
        "province",
        "is_tracked_display",
        "is_profile_complete",
        "phone",
        "last_login",
    ]

    # 列表筛选器
    list_filter = [
        "is_tracked",
        "role",
        "is_profile_complete",
        "gender",
        "is_active",
        "has_completed_cognitive_assessment",
    ]

    # 搜索字段
    search_fields = ["real_name", "phone", "wechat_openid"]

    # 排序
    ordering = ["-date_joined"]

    # 只读字段
    readonly_fields = [
        "id",
        "date_joined",
        "last_login",
        "wechat_openid",
        "wechat_unionid",
    ]

    # 字段分组
    fieldsets = (
        (
            "基本信息",
            {"fields": ("username", "password", "real_name", "role", "is_tracked")},
        ),
        (
            "微信信息",
            {"fields": ("wechat_openid", "wechat_unionid"), "classes": ("collapse",)},
        ),
        (
            "个人资料",
            {
                "fields": (
                    "gender",
                    "age",
                    "education",
                    "province",
                    "city",
                    "district",
                    "phone",
                    "is_profile_complete",
                )
            },
        ),
        (
            "测评状态",
            {
                "fields": ("has_completed_cognitive_assessment", "group"),
                "classes": ("collapse",),
            },
        ),
        (
            "测评分数",
            {
                "fields": (
                    "score_scd",
                    "score_mmse",
                    "score_moca",
                    "score_gad7",
                    "score_phq9",
                    "score_adl",
                ),
                "classes": ("collapse",),
            },
        ),
        ("情绪测试", {"fields": ("last_mood_tested_at",), "classes": ("collapse",)}),
        (
            "权限状态",
            {
                "fields": ("is_active", "is_staff", "is_superuser"),
                "classes": ("collapse",),
            },
        ),
        (
            "重要日期",
            {"fields": ("date_joined", "last_login"), "classes": ("collapse",)},
        ),
    )

    # 添加用户时的字段配置
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "real_name",
                    "role",
                    "is_tracked",
                ),
            },
        ),
    )

    def is_tracked_display(self, obj):
        """跟踪状态显示"""
        return obj.is_tracked

    is_tracked_display.short_description = "跟踪状态"
    is_tracked_display.admin_order_field = "is_tracked"
    is_tracked_display.boolean = True

    def get_queryset(self, request):
        """优化查询，隐藏超级用户"""
        qs = super().get_queryset(request)
        # 隐藏超级用户，只显示普通用户和管理员
        if not request.user.is_superuser:
            qs = qs.filter(is_superuser=False)
        return qs

    # 批量操作
    actions = ["mark_as_tracked", "mark_as_untracked", "export_selected"]

    def mark_as_tracked(self, request, queryset):
        """批量标记为已跟踪"""
        updated = queryset.update(is_tracked=True)
        self.message_user(request, f"已将 {updated} 个用户标记为已跟踪")

    mark_as_tracked.short_description = "标记为跟踪"

    def mark_as_untracked(self, request, queryset):
        """批量标记为未跟踪"""
        updated = queryset.update(is_tracked=False)
        self.message_user(request, f"已将 {updated} 个用户标记为未跟踪")

    mark_as_untracked.short_description = "跟踪"

    def export_selected(self, request, queryset):
        """导出选中的用户信息"""
        # 这里可以添加导出功能
        user_count = queryset.count()
        self.message_user(request, f"已选择 {user_count} 个用户进行导出")

    export_selected.short_description = "导出选中的用户"

    # 自定义方法显示用户信息完整度
    def profile_completion_display(self, obj):
        """资料完整度显示"""
        if obj.is_profile_complete:
            return format_html('<span style="color: #28a745;">✓ 完整</span>')
        else:
            return format_html('<span style="color: #dc3545;">✗ 不完整</span>')

    profile_completion_display.short_description = "资料完整度"
    profile_completion_display.boolean = True

    # 重写保存方法，确保用户信息完整度状态正确
    def save_model(self, request, obj, form, change):
        """保存模型时更新信息完整度"""
        obj.update_profile_complete_status()
        super().save_model(request, obj, form, change)


# 取消注册默认的 Group 模型（如果不需要）
admin.site.unregister(Group)
