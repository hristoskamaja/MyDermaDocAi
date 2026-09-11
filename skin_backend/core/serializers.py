from rest_framework import serializers

from .models import SkinCondition, Recommendation, Dermatologist


class SkinConditionSerializer(serializers.ModelSerializer):
    """
    Admin-panel serializer (React admin's Conditions page). The admin
    normally only types description/symptoms/treatment_overview in
    Macedonian, and the _en counterparts get filled in automatically (see
    core/services/translation.py via views.py) - but the _en fields are
    writable here too, so the admin can open a condition and hand-edit/
    correct the English text directly instead of only ever seeing whatever
    Gemini generated. views.py never overwrites an _en field the admin
    just typed into in the same request (see manual_en_fields there).
    """
    class Meta:
        model = SkinCondition
        fields = [
            "id",
            "key",
            "name",
            "description",
            "description_en",
            "symptoms",
            "symptoms_en",
            "treatment_overview",
            "treatment_overview_en",
            "image",
            "image_description",
            "severity",
            "category",
        ]


class RecommendationSerializer(serializers.ModelSerializer):
    """
    Admin-panel serializer (React admin's Recommendations page). name/
    description are Gemini's original English output; name_mk/description_mk
    are the Macedonian counterpart generated in the same Gemini call (see
    analyses/services/gemini_service.py) - both equally "generated", neither
    is a manual admin translation pass.
    """
    class Meta:
        model = Recommendation
        fields = [
            "id",
            "name",
            "name_mk",
            "description",
            "description_mk",
            "type",
        ]


class LocalizedRecommendationSerializer(serializers.ModelSerializer):
    """
    Patient-facing, read-only counterpart of RecommendationSerializer - used
    by core/views.py's condition_recommendations (GET only) instead of the
    admin serializer above. Resolves name/description to whichever language
    ?lang= asks for, instead of exposing the raw name/name_mk/description/
    description_mk columns. Kept separate from RecommendationSerializer so
    the admin CRUD endpoints keep plain, writable name/description fields.
    """
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Recommendation
        fields = ["id", "name", "description", "type"]

    def _wants_macedonian(self):
        request = self.context.get("request")
        lang = request.query_params.get("lang", "mk") if request else "mk"
        return lang == "mk"

    def get_name(self, obj):
        if self._wants_macedonian():
            return obj.name_mk or obj.name
        return obj.name

    def get_description(self, obj):
        if self._wants_macedonian():
            return obj.description_mk or obj.description
        return obj.description


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
