from django.contrib import admin
from .models import CognitiveAssessmentRecord

@admin.register(CognitiveAssessmentRecord)
class CognitiveAssessmentRecordAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user_id", "real_name", "gender", "age", "education",
        "province", "city", "district", "phone",
        "score_scd", "score_mmse", "score_moca", "score_gad7", "score_phq9", "score_adl", "score_sus",
        "started_at", "completed_at"
    )
    search_fields = ("user_id", "real_name", "phone")
    list_filter = ("province", "city", "education")
    readonly_fields = ("started_at", "completed_at")
    ordering = ("-started_at",)