from django.contrib import admin
from .models import ScaleConfig, ScaleResult

@admin.register(ScaleConfig)
class ScaleConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'version', 'type', 'status', 'created_at', 'updated_at')
    search_fields = ('name', 'code')
    list_filter = ('status', 'type')

@admin.register(ScaleResult)
class ScaleResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'scale_config', 'status', 'duration_ms', 'started_at', 'completed_at', 'created_at', 'updated_at')
    search_fields = ('user_id', 'scale_config__name')
    list_filter = ('status',)