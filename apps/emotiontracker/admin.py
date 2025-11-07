from django.contrib import admin
from .models import EmotionRecord

@admin.register(EmotionRecord)
class EmotionRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'depression', 'anxiety', 'energy', 'sleep', 'created_at')
    search_fields = ('user_id',)
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)