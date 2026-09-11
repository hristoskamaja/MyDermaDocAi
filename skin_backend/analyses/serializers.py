from rest_framework import serializers

from core.models import SkinCondition
from .models import Analysis, AnalysisChatMessage


class SkinConditionSerializer(serializers.ModelSerializer):
    """
    Patient-facing (read-only - only ever nested inside AnalysisDetailSerializer,
    never used to write a condition). description/symptoms/treatment_overview
    resolve to the ?lang= query param: the admin always types these in
    Macedonian, and description_en/symptoms_en/treatment_overview_en are the
    auto-translated English counterpart (see core/services/translation.py) -
    falling back to Macedonian if a translation hasn't been generated yet.
    """
    description = serializers.SerializerMethodField()
    symptoms = serializers.SerializerMethodField()
    treatment_overview = serializers.SerializerMethodField()

    class Meta:
        model = SkinCondition
        fields = [
            "id",
            "key",
            "name",
            "description",
            "symptoms",
            "treatment_overview",
            "severity",
            "category",
            "image",
        ]

    def _wants_english(self):
        request = self.context.get("request")
        lang = request.query_params.get("lang", "mk") if request else "mk"
        return lang == "en"

    def get_description(self, obj):
        if self._wants_english():
            return obj.description_en or obj.description
        return obj.description

    def get_symptoms(self, obj):
        if self._wants_english():
            return obj.symptoms_en or obj.symptoms
        return obj.symptoms

    def get_treatment_overview(self, obj):
        if self._wants_english():
            return obj.treatment_overview_en or obj.treatment_overview
        return obj.treatment_overview


class AnalysisListSerializer(serializers.ModelSerializer):
    condition_name = serializers.CharField(source="condition.name", read_only=True)
    severity = serializers.CharField(source="condition.severity", read_only=True)

    class Meta:
        model = Analysis
        fields = [
            "id",
            "analysis_key",
            "condition_name",
            "severity",
            "confidence",
            "is_low_confidence",
            "created_at",
        ]


class AnalysisDetailSerializer(serializers.ModelSerializer):
    condition = SkinConditionSerializer(read_only=True)

    class Meta:
        model = Analysis
        fields = [
            "id",
            "analysis_key",
            "user",
            "condition",
            "image",
            "confidence",
            "is_low_confidence",
            "created_at",
        ]


class AnalysisChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisChatMessage
        fields = [
            "id",
            "role",
            "content",
            "created_at",
        ]
