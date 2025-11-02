from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'publish_time', 'created_at', 'updated_at')
    search_fields = ('title', 'content')
    list_filter = ('status', 'publish_time')
    ordering = ('-publish_time',)