from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from apps.common.admin_base import ContentManageableAdmin
from apps.articles.models import Article


@admin.register(Article)
class ArticleAdmin(ContentManageableAdmin, SummernoteModelAdmin):
    """文章管理后台 - 使用内容管理基础类"""
    
    summernote_fields = ('content',)
    
    # 特有配置
    list_display = (
        'id', 'title', 'status',
        'created_at', 'updated_at',
    )
    search_fields = ('title',)
    list_filter = ('status',)
    
    # 继承自ContentManageableAdmin的fieldsets，只需要添加summernote配置
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
