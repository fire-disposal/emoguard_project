"""文章模块的 admin 配置"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """文章管理"""
    
    list_display = [
        'id', 'title', 'status_display', 
        'created_at', 'updated_at'
    ]
    
    list_filter = [
        'status', 'created_at', 'updated_at'
    ]
    
    search_fields = [
        'title', 'content'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'status')
        }),
        ('内容', {
            'fields': ('content',),
            'classes': ('wide',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def status_display(self, obj):
        """状态显示"""
        status_colors = {
            'draft': '#6c757d',
            'published': '#28a745'
        }
        status_labels = {
            'draft': '草稿',
            'published': '已发布'
        }
        
        color = status_colors.get(obj.status, '#6c757d')
        label = status_labels.get(obj.status, obj.status)
        
        return format_html(
            '<span style="color: {};">● {}</span>',
            color, label
        )
    
    status_display.short_description = '状态'
    status_display.admin_order_field = 'status'
    
    def content_summary(self, obj):
        """内容摘要"""
        if obj.content:
            return obj.content[:200] + '...' if len(obj.content) > 200 else obj.content
        return "无内容"
    
    content_summary.short_description = '内容摘要'
    
    actions = ['publish_selected', 'draft_selected']
    
    def publish_selected(self, request, queryset):
        """发布选中的文章"""
        updated = queryset.update(status='published')
        self.message_user(request, f'已发布 {updated} 篇文章')
    
    publish_selected.short_description = '发布选中的文章'
    
    def draft_selected(self, request, queryset):
        """将选中的文章设为草稿"""
        updated = queryset.update(status='draft')
        self.message_user(request, f'已将 {updated} 篇文章设为草稿')
    
    draft_selected.short_description = '设为草稿'