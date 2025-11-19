"""
用户管理后台配置 - 适配单模型设计
"""
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User
from django.contrib import admin

admin.site.site_title = "情绪监测系统"
admin.site.site_header = "情绪监测系统"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户管理后台"""

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(is_staff=True)

    # 列表显示字段
    list_display = (
        "username",
        "real_name",
        "gender",
        "age",
        "education",
        "province",
        "city",
        "phone",
        "score_scd", 
        "score_mmse", 
        "score_moca", 
        "is_profile_complete",
        "last_mood_tested_at",
    )
    list_display_links = ("username",)

    # 搜索字段
    search_fields = (
        "username",
        "real_name",
        "email",
        "wechat_openid",
        "wechat_unionid",
        "phone",
    )

    # 过滤字段
    list_filter = ("role", "gender", "is_active", "is_staff", "date_joined")

    # 排序
    ordering = ("-date_joined",)

    # 分页
    list_per_page = 20

    # 字段分组
    fieldsets = (
        ("账号信息", {"fields": ("username", "email", "password")}),
        (
            "基础资料",
            {
                "fields": (
                    "real_name",
                    "gender",
                    "age",
                    "education",
                    "province",
                    "city",
                    "district",
                    "phone",
                    "is_profile_complete",
                    "score_scd",
                    "score_mmse",
                    "score_moca",
                    "score_gad7",
                    "score_phq9",
                    "score_adl",
                    "last_mood_tested_at",
                ),
                "description": "请完善用户的基本信息，便于后续服务。测评分数可由管理员直接编辑。",
            },
        ),
        (
            "微信相关（技术字段，通常可忽略）",
            {
                "fields": ("wechat_openid", "wechat_unionid"),
                "classes": ("collapse",),
                "description": "微信小程序用户相关信息，仅技术人员关注。",
            },
        ),
        (
            "权限设置",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "description": "如无特殊需求，保持默认即可。",
            },
        ),
        (
            "时间信息",
            {"fields": ("date_joined", "last_login"), "classes": ("collapse",)},
        ),
    )

    # 只读字段
    readonly_fields = ("date_joined", "last_login")

    @admin.display(description="用户类型")
    def user_type_display(self, obj):
        """显示用户类型"""
        if obj.is_wechat_user:
            return "微信用户"
        return "密码用户"

    @admin.display(description="微信OpenID", ordering="wechat_openid")
    def wechat_openid_short(self, obj):
        """显示微信OpenID的简短形式"""
        if obj.wechat_openid:
            return format_html(
                '<span title="{}">{}...</span>',
                obj.wechat_openid,
                obj.wechat_openid[:8],
            )
        return "-"
