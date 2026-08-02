from rest_framework import serializers

from .models import SkinCondition, Recommendation


class SkinConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkinCondition
        fields = [
            "id",
            "key",
            "name",
            "description",
            "symptoms",
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
