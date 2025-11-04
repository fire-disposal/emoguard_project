from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Article


@admin.register(Article)
class ArticleAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)  

    list_display = (
        'id', 'title', 'status',
        'created_at', 'updated_at',
    )
    search_fields = ('title',)
    list_filter = ('status',)
    ordering = ('-created_at',)
    list_per_page = 20 

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

    readonly_fields = ("created_at", "updated_at")  
    
