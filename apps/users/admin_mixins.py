"""通用的用户管理 mixin 类"""
from django.contrib import admin
from django.db.models import Q
from django.utils.html import format_html
from apps.users.models import User


class UserRealNameSearchMixin:
    """支持通过用户真名查找的 mixin 类"""
    
    def get_search_results(self, request, queryset, search_term):
        """重写搜索功能，支持通过用户真名搜索"""
        # 首先获取父类的搜索结果
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        
        # 如果有搜索词，并且模型有 user_id 字段，则通过用户真名进行额外搜索
        if search_term and hasattr(self.model, 'user_id'):
            # 查找用户真名或用户名匹配的用户
            matching_users = User.objects.filter(
                Q(real_name__icontains=search_term) |
                Q(username__icontains=search_term)
            )
            
            if matching_users.exists():
                # 获取这些用户的 UUID
                user_uuids = list(matching_users.values_list('id', flat=True))
                # 添加 user_id 在这些 UUID 中的条件
                queryset = queryset | self.model.objects.filter(user_id__in=user_uuids)
                use_distinct = True
        
        return queryset, use_distinct
    
    def get_list_display(self, request):
        """获取列表显示字段，用用户真名替换 user_id"""
        list_display = list(super().get_list_display(request) if hasattr(super(), 'get_list_display') else [])
        
        # 如果列表中有 user_id，替换为 user_real_name
        if 'user_id' in list_display:
            index = list_display.index('user_id')
            list_display[index] = 'user_real_name'
        
        return list_display
    
    def get_list_filter(self, request):
        """获取过滤字段"""
        list_filter = list(super().get_list_filter(request) if hasattr(super(), 'get_list_filter') else [])
        return list_filter
    
    def user_real_name(self, obj):
        """显示用户真名"""
        if hasattr(obj, 'user_id'):
            try:
                user = User.objects.get(id=obj.user_id)
                return user.real_name or user.username
            except User.DoesNotExist:
                return "用户不存在"
        return "-"
    
    user_real_name.short_description = '用户姓名'
    user_real_name.admin_order_field = 'user_id'


class UserRealNameFilter(admin.SimpleListFilter):
    """用户真名过滤器"""
    title = '用户姓名'
    parameter_name = 'user_real_name'
    
    def lookups(self, request, model_admin):
        """返回过滤选项"""
        # 获取所有相关的用户
        if hasattr(model_admin.model, 'user_id'):
            user_ids = model_admin.model.objects.values_list('user_id', flat=True).distinct()
            users = User.objects.filter(id__in=user_ids).order_by('real_name', 'username')
            
            lookups = []
            for user in users:
                display_name = user.real_name or user.username
                lookups.append((str(user.id), display_name))
            return lookups
        return []
    
    def queryset(self, request, queryset):
        """过滤查询集"""
        if self.value():
            return queryset.filter(user_id=self.value())
        return queryset


class UUIDUserAdminMixin(UserRealNameSearchMixin):
    """针对使用 UUID 作为 user_id 的模型的 admin mixin"""
    
    search_fields = []
    list_display = []
    
    def get_queryset(self, request):
        """优化查询，预取用户信息"""
        qs = super().get_queryset(request)
        if hasattr(self.model, 'user_id'):
            # 这里可以添加 select_related 或 prefetch_related 如果有关联关系
            pass
        return qs
    
    def lookup_allowed(self, lookup, value):
        """允许通过用户真名进行查找"""
        if lookup == 'user_real_name':
            return True
        return super().lookup_allowed(lookup, value)


class ForeignKeyUserAdminMixin(UserRealNameSearchMixin):
    """针对使用 ForeignKey 关联用户的模型的 admin mixin"""
    
    def user_real_name(self, obj):
        """显示用户真名"""
        if hasattr(obj, 'user') and obj.user:
            return obj.user.real_name or obj.user.username
        return "匿名用户"
    
    user_real_name.short_description = '用户姓名'
    user_real_name.admin_order_field = 'user__real_name'