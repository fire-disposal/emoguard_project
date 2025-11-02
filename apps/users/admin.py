"""
用户管理后台配置
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    """用户资料内联编辑"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = '用户资料'
    fields = ('nickname', 'avatar', 'gender', 'birthday', 'bio', 'phone', 'address')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户管理后台"""
    
    # 列表显示字段
    list_display = (
        'id', 'username', 'email', 'role', 'login_type', 
        'wechat_openid_short', 'is_active', 'is_staff', 'date_joined'
    )
    list_display_links = ('id', 'username')
    
    # 搜索字段
    search_fields = ('username', 'email', 'wechat_openid', 'wechat_unionid')
    
    # 过滤字段
    list_filter = ('role', 'login_type', 'is_active', 'is_staff', 'date_joined')
    
    # 排序
    ordering = ('-date_joined',)
    
    # 分页
    list_per_page = 20
    
    # 内联编辑
    inlines = (UserProfileInline,)
    
    # 字段分组
    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'email', 'password')
        }),
        ('微信信息', {
            'fields': ('wechat_openid', 'wechat_unionid'),
            'classes': ('collapse',),
            'description': '微信小程序用户相关信息'
        }),
        ('权限信息', {
            'fields': ('role', 'login_type', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('时间信息', {
            'fields': ('date_joined',),
            'classes': ('collapse',)
        }),
    )
    
    # 只读字段
    readonly_fields = ('date_joined',)
    
    def wechat_openid_short(self, obj):
        """显示微信OpenID的简短形式"""
        if obj.wechat_openid:
            return format_html(
                '<span title="{}">{}...</span>',
                obj.wechat_openid,
                obj.wechat_openid[:8]
            )
        return "-"
    
    wechat_openid_short.short_description = '微信OpenID'
    wechat_openid_short.admin_order_field = 'wechat_openid'
    
    def get_queryset(self, request):
        """优化查询，减少数据库查询次数"""
        return super().get_queryset(request).select_related('profile')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """用户资料管理后台"""
    
    # 列表显示字段
    list_display = (
        'id', 'user_link', 'nickname', 'gender', 'birthday', 
        'created_at', 'updated_at'
    )
    list_display_links = ('id', 'user_link')
    
    # 搜索字段
    search_fields = ('nickname', 'user__username', 'user__email', 'user__wechat_openid')
    
    # 过滤字段
    list_filter = ('gender', 'created_at', 'updated_at')
    
    # 排序
    ordering = ('-created_at',)
    
    # 分页
    list_per_page = 20
    
    # 只读字段
    readonly_fields = ('created_at', 'updated_at')
    
    def user_link(self, obj):
        """显示用户链接"""
        return format_html(
            '<a href="/admin/users/user/{}/change/">{}</a>',
            obj.user.id,
            obj.user.username
        )
    
    user_link.short_description = '用户'
    user_link.admin_order_field = 'user__username'
    
    def get_queryset(self, request):
        """优化查询，减少数据库查询次数"""
        return super().get_queryset(request).select_related('user')
