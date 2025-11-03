"""
用户管理后台配置 - 适配单模型设计
"""
from django.contrib import admin
admin.site.site_title = "认知照顾情绪监测系统后台"
admin.site.site_header = "认知照顾情绪监测系统管理"
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户管理后台"""
    
    # 列表显示字段
    list_display = (
        'id', 'username', 'nickname', 'real_name', 'email', 'role', 
        'user_type_display', 'wechat_openid_short', 'is_active', 'is_staff', 'date_joined'
    )
    list_display_links = ('id', 'username')
    
    # 搜索字段
    search_fields = ('username', 'nickname', 'real_name', 'email', 'wechat_openid', 'wechat_unionid', 'phone')
    
    # 过滤字段
    list_filter = ('role', 'gender', 'education', 'is_active', 'is_staff', 'date_joined')
    
    # 排序
    ordering = ('-date_joined',)
    
    # 分页
    list_per_page = 20
    
    # 字段分组
    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'email', 'password')
        }),
        ('用户资料', {
            'fields': ('nickname', 'real_name', 'avatar', 'gender', 'birthday', 'bio')
        }),
        ('微信信息', {
            'fields': ('wechat_openid', 'wechat_unionid'),
            'classes': ('collapse',),
            'description': '微信小程序用户相关信息'
        }),
        ('联系信息', {
            'fields': ('phone', 'address'),
            'classes': ('collapse',)
        }),
        ('教育与职业', {
            'fields': ('education', 'occupation'),
            'classes': ('collapse',)
        }),
        ('权限信息', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('时间信息', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    # 只读字段
    readonly_fields = ('date_joined', 'last_login')
    
    @admin.display(description='用户类型')
    def user_type_display(self, obj):
        """显示用户类型"""
        if obj.is_wechat_user:
            return '微信用户'
        return '密码用户'
    
    @admin.display(description='微信OpenID', ordering='wechat_openid')
    def wechat_openid_short(self, obj):
        """显示微信OpenID的简短形式"""
        if obj.wechat_openid:
            return format_html(
                '<span title="{}">{}...</span>',
                obj.wechat_openid,
                obj.wechat_openid[:8]
            )
        return "-"
