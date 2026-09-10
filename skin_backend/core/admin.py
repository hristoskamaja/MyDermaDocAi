from django.contrib import admin

from .models import SkinCondition, Recommendation, ConditionRecommendation, Dermatologist


@admin.register(SkinCondition)
class SkinConditionAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "severity", "category")
    search_fields = ("name", "key")
    list_filter = ("severity", "category")


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ("name", "type")
    list_filter = ("type",)


@admin.register(ConditionRecommendation)
class ConditionRecommendationAdmin(admin.ModelAdmin):
    list_display = ("condition", "recommendation")


@admin.register(Dermatologist)
class DermatologistAdmin(admin.ModelAdmin):
    list_display = ("name", "clinic_name", "city", "phone", "is_active")
    search_fields = ("name", "clinic_name", "city")
    list_filter = ("is_active", "city")
