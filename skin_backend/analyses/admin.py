from django.contrib import admin

from .models import Analysis


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ("analysis_key", "user", "condition", "confidence", "is_low_confidence", "created_at")
    list_filter = ("is_low_confidence", "condition")
    search_fields = ("analysis_key",)
