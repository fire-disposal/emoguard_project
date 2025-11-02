from django.contrib import admin
from .models import MoodJournal

@admin.register(MoodJournal)
class MoodJournalAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'mood_score', 'mood_name', 'mood_emoji', 'record_date', 'created_at')
    search_fields = ('user__username', 'mood_name', 'text')
    list_filter = ('mood_score', 'record_date', 'created_at')