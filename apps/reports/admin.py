from django.contrib import admin
from .models import HealthReport

@admin.register(HealthReport)
class HealthReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'assessment_id', 'report_type', 'overall_risk', 'created_at')
    search_fields = ('user_id', 'assessment_id', 'report_type', 'overall_risk')
    list_filter = ('report_type', 'overall_risk', 'created_at')