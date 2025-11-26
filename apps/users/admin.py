"""
用户管理后台配置 - 适配单模型设计
"""

from django.utils.html import format_html
from .models import User
from django.contrib import admin
from import_export.admin import ExportActionModelAdmin
from import_export import resources, fields
from apps.users.demographic_export import build_excel_with_demographics, build_csv_with_demographics

admin.site.site_title = "情绪监测系统"
admin.site.site_header = "情绪监测系统"



class UserResource(resources.ModelResource):
    """用户导出资源（人口学信息与业务字段分离，避免重复）"""
    id = fields.Field(column_name="用户ID", attribute="id")
    username = fields.Field(column_name="用户名", attribute="username")
    real_name = fields.Field(column_name="真实姓名", attribute="real_name")
    gender = fields.Field(column_name="性别", attribute="gender")
    age = fields.Field(column_name="年龄", attribute="age")
    education = fields.Field(column_name="学历", attribute="education")
    province = fields.Field(column_name="省份", attribute="province")
    city = fields.Field(column_name="城市", attribute="city")
    district = fields.Field(column_name="区县", attribute="district")
    phone = fields.Field(column_name="手机号", attribute="phone")
    is_profile_complete = fields.Field(column_name="信息已完善", attribute="is_profile_complete")
    role = fields.Field(column_name="角色", attribute="role")
    score_scd = fields.Field(column_name="SCD分数", attribute="score_scd")
    score_mmse = fields.Field(column_name="MMSE分数", attribute="score_mmse")
    score_moca = fields.Field(column_name="MoCA分数", attribute="score_moca")
    score_gad7 = fields.Field(column_name="GAD7分数", attribute="score_gad7")
    score_phq9 = fields.Field(column_name="PHQ9分数", attribute="score_phq9")
    score_adl = fields.Field(column_name="ADL分数", attribute="score_adl")
    last_mood_tested_at = fields.Field(column_name="上次情绪测试时间", attribute="last_mood_tested_at")

    class Meta:
        model = User
        fields = [
            "id", "username", "real_name", "gender", "age", "education", "province", "city", "district", "phone",
            "is_profile_complete", "role", "score_scd", "score_mmse", "score_moca", "score_gad7", "score_phq9", "score_adl", "last_mood_tested_at"
        ]
        export_order = fields
        skip_unchanged = True

@admin.register(User)
class UserAdmin(ExportActionModelAdmin):
    """用户管理后台"""

    resource_class = UserResource

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

    actions = ["export_selected_excel", "export_selected_csv"]

    def export_selected_excel(self, request, queryset):
        """导出用户为Excel格式（仅额外导出微信字段、信息完善状态和上次情绪测试时间）"""
        extra_field_order = [
            "wechat_openid", "wechat_unionid", "is_profile_complete", "last_mood_tested_at"
        ]
        extra_field_titles = [
            "微信OpenID", "微信UnionID", "信息已完善", "上次情绪测试时间"
        ]
        def get_user_id(record):
            return record.id
        return build_excel_with_demographics(queryset, get_user_id, extra_field_order, extra_field_titles)
    export_selected_excel.short_description = "导出为Excel"

    def export_selected_csv(self, request, queryset):
        """导出用户为CSV格式（仅额外导出微信字段、信息完善状态和上次情绪测试时间）"""
        extra_field_order = [
            "wechat_openid", "wechat_unionid", "is_profile_complete", "last_mood_tested_at"
        ]
        extra_field_titles = [
            "微信OpenID", "微信UnionID", "信息已完善", "上次情绪测试时间"
        ]
        def get_user_id(record):
            return record.id
        return build_csv_with_demographics(queryset, get_user_id, extra_field_order, extra_field_titles)
    export_selected_csv.short_description = "导出为CSV"

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
