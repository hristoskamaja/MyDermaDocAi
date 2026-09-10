from rest_framework import serializers

from .models import SkinCondition, Recommendation, Dermatologist


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
            "image",
            "image_description",
            "severity",
            "category",
        ]


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = [
            "id",
            "name",
            "description",
            "type",
        ]


class DermatologistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dermatologist
        fields = [
            "id",
            "name",
            "clinic_name",
            "city",
            "address",
            "phone",
            "website",
            "notes",
            "is_active",
            "created_at",
        ]
