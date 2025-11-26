from django.contrib import admin
from apps.scales.models import ScaleResult

@admin.register(ScaleResult)
class ScaleResultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_id",
        "scale_code",
        "score",
        "started_at",
        "completed_at",
        "created_at",
    )
    search_fields = ("user_id", "scale_code")
    list_filter = ("scale_code", "started_at", "completed_at", "created_at")
