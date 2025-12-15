"""
统一的Admin Mixin模块
提供用户信息展示和导出功能的统一实现
"""
from django.utils.html import format_html
from apps.users.demographic_export import (
    get_demographic_info,
    build_excel_with_demographics,
    build_csv_with_demographics
)


class UserInfoDisplayMixin:
    """统一用户信息展示mixin"""
    
    def user_info(self, obj):
        """显示用户信息完整形式（用户真名 + 性别 + 年龄 + 分组）"""
        user_info = get_demographic_info(obj.user_id)
        real_name = user_info.get("real_name", "未知")
        gender = user_info.get("gender", "未知")
        age = user_info.get("age", "未知")
        group = user_info.get("group", "")
        group_display = f"【{group}】" if group else ""
        return format_html(
            "{}{}{}{}",
            real_name,
            f" | {gender}" if gender != "未知" else "",
            f" | {age}岁" if age != "未知" else "",
            group_display
        )
    user_info.short_description = "用户信息"
    
    def user_info_short(self, obj):
        """显示用户信息简短形式（用户真名+分组）"""
        user_info = get_demographic_info(obj.user_id)
        real_name = user_info.get("real_name", "未知")
        group = user_info.get("group", "")
        group_display = f"【{group}】" if group else ""
        if real_name != "未知" and len(real_name) > 4:
            real_name = real_name[:4] + "..."
        return format_html(
            "{}{}",
            real_name,
            group_display
        )
    user_info_short.short_description = "用户信息"


class ExportWithDemographicsMixin:
    """统一导出功能mixin"""
    
    export_extra_fields = []  # 子类需要定义导出的额外字段
    export_extra_titles = []  # 子类需要定义对应的标题
    
    def get_export_extra_fields(self):
        """获取导出的额外字段配置"""
        return self.export_extra_fields
    
    def get_export_extra_titles(self):
        """获取导出的额外字段标题"""
        return self.export_extra_titles
    
    def export_selected_excel(self, request, queryset):
        """统一Excel导出方法"""
        extra_field_order = self.get_export_extra_fields()
        extra_field_titles = self.get_export_extra_titles()
        
        def get_user_id(record):
            return getattr(record, 'user_id', None)
        
        return build_excel_with_demographics(
            queryset, get_user_id, extra_field_order, extra_field_titles
        )
    export_selected_excel.short_description = "导出为Excel"
    
    def export_selected_csv(self, request, queryset):
        """统一CSV导出方法"""
        extra_field_order = self.get_export_extra_fields()
        extra_field_titles = self.get_export_extra_titles()
        
        def get_user_id(record):
            return getattr(record, 'user_id', None)
        
        return build_csv_with_demographics(
            queryset, get_user_id, extra_field_order, extra_field_titles
        )
    export_selected_csv.short_description = "导出为CSV"


class BaseAdminMixin(UserInfoDisplayMixin, ExportWithDemographicsMixin):
    """基础Admin Mixin，组合用户信息展示和导出功能"""
    pass