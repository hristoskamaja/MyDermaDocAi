from rest_framework import serializers

from core.models import SkinCondition
from .models import Analysis, AnalysisChatMessage


class SkinConditionSerializer(serializers.ModelSerializer):
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
