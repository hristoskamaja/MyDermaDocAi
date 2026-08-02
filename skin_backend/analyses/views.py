import uuid

from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import SkinCondition, Recommendation, ConditionRecommendation
from .models import Analysis
from .serializers import AnalysisListSerializer, AnalysisDetailSerializer
from .services.skin_model_service import predict_skin_condition, SkinModelPredictionError
from .services.gemini_service import generate_recommendations_with_gemini


# ---------------------------------------------------------------------------
# HELPERS (истите како во leafscan: is_admin_user, can_access_analysis,
# generate_analysis_key)
# ---------------------------------------------------------------------------

def is_admin_user(request):
    return (
        request.user.is_staff
        or request.user.is_superuser
        or getattr(request.user, "role", None) == "ADMIN"
    )


def can_access_analysis(request, analysis):
    return is_admin_user(request) or analysis.user_id == request.user.id


def generate_analysis_key():
    return f"SK-{uuid.uuid4().hex[:8].upper()}"


def condition_has_recommendations(condition):
    if not condition:
        return False
    return ConditionRecommendation.objects.filter(condition=condition).exists()


def save_gemini_recommendations_for_condition(condition, recommendations_data):
    if not condition or not recommendations_data:
        return []

    saved = []

    for item in recommendations_data:
        name = item.get("name")
        description = item.get("description")
        rec_type = item.get("type")

        if not name or not description or not rec_type:
            continue

        recommendation, created = Recommendation.objects.get_or_create(
            name=name,
            type=rec_type,
            defaults={"description": description},
        )

        if not created and not recommendation.description:
            recommendation.description = description
            recommendation.save(update_fields=["description"])

        ConditionRecommendation.objects.get_or_create(
            condition=condition,
            recommendation=recommendation,
        )

        saved.append(recommendation)

    return saved


def generate_recommendations_only_if_missing(condition):
    """
    Gemini се повикува само ако состојбата сеуште нема препораки зачувани -
    исто како третманите во leafscan (не сакаме различни совети на секое
    скенирање на истата состојба).
    """

    if not condition:
        return {"generated": False, "reason": "Missing condition.", "count": 0}

    if condition_has_recommendations(condition):
        existing_count = ConditionRecommendation.objects.filter(condition=condition).count()
        return {
            "generated": False,
            "reason": "Recommendations already exist for this condition.",
            "count": existing_count,
        }

    recommendations_data = generate_recommendations_with_gemini(
        condition_name=condition.name,
        severity=condition.severity or "MEDIUM",
    )

    saved = save_gemini_recommendations_for_condition(condition, recommendations_data)

    return {
        "generated": True,
        "reason": "Recommendations generated successfully.",
        "count": len(saved),
    }


# ---------------------------------------------------------------------------
# ANALYSES
# ---------------------------------------------------------------------------

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def scan_skin(request):
    """
    ГЛАВНИОТ endpoint - еквивалент на scan_plant() од leafscan.

    Тек: слика -> локален модел (skin_model_service) -> бара SkinCondition
    по `key` -> зачувува Analysis -> генерира Gemini препораки (само прв пат
    за таа состојба) -> враќа сè заедно.

    Додека analyses/services/ai_model/skin_model.pt сè уште не постои
    (пред да го натренираш), ова ќе враќа 502 со јасна порака - тоа е
    очекувано, не е баг.
    """

    image = request.FILES.get("image")

    if not image:
        return Response(
            {"image": "This field is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        prediction = predict_skin_condition(image)

        if hasattr(image, "seek"):
            image.seek(0)

    except SkinModelPredictionError as error:
        return Response(
            {
                "detail": "AI prediction failed.",
                "error": str(error),
            },
            status=status.HTTP_502_BAD_GATEWAY,
        )

    condition_key = prediction.get("condition_key")

    condition = SkinCondition.objects.filter(key=condition_key).first()

    if not condition:
        return Response(
            {
                "condition": (
                    f"Condition '{condition_key}' does not exist in database. "
                    "Изврши `python manage.py seed_skin_conditions` прво."
                ),
                "prediction": prediction,
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    analysis = Analysis.objects.create(
        analysis_key=generate_analysis_key(),
        user=request.user,
        condition=condition,
        image=image,
        confidence=prediction.get("confidence"),
        is_low_confidence=prediction.get("is_low_confidence", False),
    )

    recommendation_generation = generate_recommendations_only_if_missing(condition)

    serializer = AnalysisDetailSerializer(analysis)

    return Response(
        {
            "message": "Analysis created successfully.",
            "prediction": prediction,
            "recommendation_generation": recommendation_generation,
            "analysis": serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_analyses(request):
    analyses = Analysis.objects.filter(
        user=request.user
    ).select_related("condition").order_by("-created_at")

    serializer = AnalysisListSerializer(analyses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analysis_detail(request, id):
    analysis = get_object_or_404(
        Analysis.objects.select_related("user", "condition"),
        id=id,
    )

    if not can_access_analysis(request, analysis):
        return Response(
            {"detail": "You do not have permission to access this analysis."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = AnalysisDetailSerializer(analysis)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_analyses(request):
    if not is_admin_user(request):
        return Response(
            {"detail": "Admin permission required."},
            status=status.HTTP_403_FORBIDDEN,
        )

    analyses = Analysis.objects.all().select_related("user", "condition").order_by("-created_at")
    serializer = AnalysisListSerializer(analyses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
