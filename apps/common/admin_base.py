"""
统一的Admin基础组件 - 提供高度复用化的管理后台实现
"""
from django.utils.html import format_html
from import_export.admin import ExportActionModelAdmin
from import_export import resources, fields
from apps.users.demographic_export import (
    get_demographic_info,
    build_excel_with_demographics,
    build_csv_with_demographics
)


class BaseResource(resources.ModelResource):
    """统一的基础资源类，提供通用字段和格式化方法"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 动态添加常用字段
        self._setup_common_fields()
    
    def _setup_common_fields(self):
        """设置通用字段"""
        # ID字段
        if hasattr(self._meta.model, 'id'):
            self.fields['id'] = fields.Field(
                column_name="记录ID", 
                attribute="id"
            )
        
        # 用户ID字段
        if hasattr(self._meta.model, 'user_id'):
            self.fields['user_id_display'] = fields.Field(
                column_name="用户ID", 
                attribute="user_id"
            )
        
        # 时间字段
        time_fields = ['created_at', 'updated_at', 'started_at', 'completed_at', 'record_date']
        for field_name in time_fields:
            if hasattr(self._meta.model, field_name):
                self.fields[field_name] = fields.Field(
                    column_name=self._get_chinese_title(field_name), 
                    attribute=field_name
                )
    
    def _get_chinese_title(self, field_name):
        """获取字段的中文标题"""
        title_map = {
            'created_at': '创建时间',
            'updated_at': '更新时间', 
            'started_at': '开始时间',
            'completed_at': '完成时间',
            'record_date': '记录日期'
        }
        return title_map.get(field_name, field_name)
    
    def dehydrate_created_at(self, obj):
        """统一的时间格式化方法"""
        if hasattr(obj, 'created_at') and obj.created_at:
            return obj.created_at.strftime("%Y年%m月%d日 %H点%M分%S秒")
        return ""
    
    def dehydrate_updated_at(self, obj):
        """统一的时间格式化方法"""
        if hasattr(obj, 'updated_at') and obj.updated_at:
            return obj.updated_at.strftime("%Y年%m月%d日 %H点%M分%S秒")
        return ""
    
    def dehydrate_started_at(self, obj):
        """统一的时间格式化方法"""
        if hasattr(obj, 'started_at') and obj.started_at:
            return obj.started_at.strftime("%Y年%m月%d日 %H点%M分%S秒")
        return ""
    
    def dehydrate_completed_at(self, obj):
        """统一的时间格式化方法"""
        if hasattr(obj, 'completed_at') and obj.completed_at:
            return obj.completed_at.strftime("%Y年%m月%d日 %H点%M分%S秒")
        return ""
    
    def dehydrate_record_date(self, obj):
        """统一的时间格式化方法"""
        if hasattr(obj, 'record_date') and obj.record_date:
            return obj.record_date.strftime("%Y年%m月%d日 %H点%M分%S秒")
        return ""
    
    def dehydrate_user_id_display(self, obj):
        """用户ID显示"""
        if hasattr(obj, 'user_id'):
            return str(obj.user_id)
        return ""
    
    def dehydrate_duration(self, obj):
        """计算答题时长"""
        if (hasattr(obj, 'started_at') and hasattr(obj, 'created_at') and 
            obj.started_at and obj.created_at):
            delta = (obj.created_at - obj.started_at).total_seconds()
            return int(delta)
        return ""


class UserInfoMixin:
    """统一用户信息展示mixin - 增强版"""
    
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


class ExportMixin:
    """统一导出功能mixin - 增强版"""
    
    export_extra_fields = []  # 子类需要定义导出的额外字段
    export_extra_titles = []  # 子类需要定义对应的标题
    
    def get_export_extra_fields(self):
        """获取导出的额外字段配置"""
        if hasattr(self, '_export_extra_fields'):
            return self._export_extra_fields
        return self.export_extra_fields
    
    def get_export_extra_titles(self):
        """获取导出的额外字段标题"""
        if hasattr(self, '_export_extra_titles'):
            return self._export_extra_titles
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


class BaseModelAdmin(UserInfoMixin, ExportMixin, ExportActionModelAdmin):
    """基础ModelAdmin类 - 提供最常用的配置"""
    
    # 通用配置
    list_per_page = 25
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    
    # 通用搜索和过滤字段
    search_fields = ("user_id",)
    list_filter = ("created_at",)
    
    # 通用列表显示
    list_display = ("id", "user_info", "created_at")
    list_display_links = ("id", "user_info")
    
    # 通用导出配置
    export_extra_fields = ["id", "created_at"]
    export_extra_titles = ["记录ID", "创建时间"]
    
    actions = ["export_selected_excel", "export_selected_csv"]


class TimeBasedAdmin(BaseModelAdmin):
    """基于时间字段的Admin基类"""
    
    def get_list_display(self, request):
        """动态生成列表显示字段，只包含模型存在的字段"""
        base_fields = ["id", "user_info"]
        time_fields = []
        
        if hasattr(self.model, 'started_at'):
            time_fields.append("started_at")
        if hasattr(self.model, 'completed_at'):
            time_fields.append("completed_at")
        if hasattr(self.model, 'created_at'):
            time_fields.append("created_at")
        if hasattr(self.model, 'record_date') and 'record_date' not in time_fields:
            time_fields.append("record_date")
            
        return base_fields + time_fields
    
    def get_readonly_fields(self, request, obj=None):
        """动态生成只读字段，只包含模型存在的字段"""
        readonly_fields = ["created_at"]  # 默认创建时间是只读的
        
        if hasattr(self.model, 'started_at'):
            readonly_fields.append("started_at")
        if hasattr(self.model, 'completed_at'):
            readonly_fields.append("completed_at")
        if hasattr(self.model, 'record_date'):
            readonly_fields.append("record_date")
            
        return tuple(readonly_fields)
    
    def get_list_filter(self, request):
        """动态生成过滤字段，只包含模型存在的字段"""
        list_filter = []
        
        if hasattr(self.model, 'started_at'):
            list_filter.append("started_at")
        if hasattr(self.model, 'completed_at'):
            list_filter.append("completed_at")
        if hasattr(self.model, 'created_at'):
            list_filter.append("created_at")
        if hasattr(self.model, 'record_date'):
            list_filter.append("record_date")
            
        return tuple(list_filter)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 动态设置导出配置
        self._export_extra_fields = self._get_dynamic_export_fields()
        self._export_extra_titles = self._get_dynamic_export_titles()
    
    def _get_dynamic_export_fields(self):
        """动态生成导出字段"""
        fields = ["id"]
        if hasattr(self.model, 'started_at'):
            fields.append("started_at")
        if hasattr(self.model, 'completed_at'):
            fields.append("completed_at")
        if hasattr(self.model, 'created_at'):
            fields.append("created_at")
        if hasattr(self.model, 'record_date'):
            fields.append("record_date")
        return fields
    
    def _get_dynamic_export_titles(self):
        """动态生成导出字段标题"""
        titles = ["记录ID"]
        if hasattr(self.model, 'started_at'):
            titles.append("开始时间")
        if hasattr(self.model, 'completed_at'):
            titles.append("完成时间")
        if hasattr(self.model, 'created_at'):
            titles.append("创建时间")
        if hasattr(self.model, 'record_date'):
            titles.append("记录日期")
        return titles


class ScoreBasedAdmin(BaseModelAdmin):
    """基于评分字段的Admin基类"""
    
    # 评分相关的通用配置
    list_filter = ("created_at",)
    
    def get_list_display(self, request):
        """动态生成列表显示字段"""
        base_fields = ["id", "user_info"]
        score_fields = self._get_score_fields()
        time_fields = ["created_at"]
        return base_fields + score_fields + time_fields
    
    def _get_score_fields(self):
        """获取评分字段"""
        score_fields = []
        for field in self.model._meta.fields:
            if 'score' in field.name or field.name in ['depression', 'anxiety', 'energy', 'sleep']:
                score_fields.append(field.name)
        return score_fields


class ContentManageableAdmin(BaseModelAdmin):
    """内容管理Admin基类 - 适用于文章、通知等"""
    
    # 内容管理通用配置
    list_display = ("id", "title", "status", "created_at", "updated_at")
    list_display_links = ("id", "title")
    search_fields = ("title",)
    list_filter = ("status", "created_at")
    readonly_fields = ("created_at", "updated_at")
    
    # 通用字段分组
    fieldsets = (
        ("基本信息", {
            "fields": ("title", "status"),
            "classes": ("wide",),
        }),
        ("内容", {
            "fields": ("content",),
            "classes": ("wide",),
        }),
    )
    
    # 导出配置
    export_extra_fields = ["id", "title", "status", "created_at", "updated_at"]
    export_extra_titles = ["记录ID", "标题", "状态", "创建时间", "更新时间"]