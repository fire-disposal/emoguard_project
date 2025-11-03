from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Article


@admin.register(Article)
class ArticleAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)  # ✅ 指定富文本字段

    list_display = (
        'id', 'title', 'status', 'publish_time',
        'created_at', 'updated_at',
    )
    search_fields = ('title',)  # ✅ 实际上搜索 content 性能差，建议移除 content
    list_filter = ('status', 'publish_time')
    ordering = ('-publish_time',)
    list_per_page = 20  # 每页显示20条记录

    # ✅ 优化后台表单布局 - 更宽的布局
    fieldsets = (
        ("基本信息", {
            "fields": ("title", "status", "cover_image"),
            "classes": ("wide",),  # 使用更宽的布局
        }),
        ("内容", {
            "fields": ("content",),
            "classes": ("wide",),  # 内容区域使用全宽
        }),
        ("时间和封面", {
            "fields": ("publish_time",),
            "classes": ("wide", "collapse"),  # ✅ 默认折叠，保持干净
        }),
    )

    # ✅ 自动填充创建/更新时间（如果模型支持 auto_now/now_add）
    readonly_fields = ("created_at", "updated_at")  # 模型里要有这两个字段
    
    # 自定义表单样式
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)  # 可以添加自定义CSS
        }
