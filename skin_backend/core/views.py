from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import SkinCondition, Recommendation, ConditionRecommendation
from .serializers import SkinConditionSerializer, RecommendationSerializer


def is_admin_user(request):
    return (
        request.user.is_staff
        or request.user.is_superuser
        or getattr(request.user, "role", None) == "ADMIN"
    )


def admin_required_response():
    return Response(
        {"detail": "Admin permission required."},
        status=status.HTTP_403_FORBIDDEN
    )


# SKIN CONDITIONS
# Еквивалент на Diseases страницата во leafscan_web/src/pages/Diseases -
# React admin панелот тука листа/уредува состојби наместо болести на растенија.

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def conditions_collection(request):
    if request.method == "GET":
        conditions = SkinCondition.objects.all().order_by("name")

        search = request.query_params.get("search")
        category = request.query_params.get("category")
        severity = request.query_params.get("severity")

        if search:
            conditions = conditions.filter(name__icontains=search)

        if category:
            conditions = conditions.filter(category=category)

        if severity:
            conditions = conditions.filter(severity=severity)

        serializer = SkinConditionSerializer(conditions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        if not is_admin_user(request):
            return admin_required_response()

        serializer = SkinConditionSerializer(data=request.data)

        if serializer.is_valid():
            condition = serializer.save()
            return Response(
                {
                    "message": "Condition created successfully.",
                    "condition": SkinConditionSerializer(condition).data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def condition_detail(request, id):
    condition = get_object_or_404(SkinCondition, id=id)

    if request.method == "GET":
        serializer = SkinConditionSerializer(condition)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if not is_admin_user(request):
        return admin_required_response()

    if request.method in ("PUT", "PATCH"):
        partial = request.method == "PATCH"
        serializer = SkinConditionSerializer(condition, data=request.data, partial=partial)

        if serializer.is_valid():
            condition = serializer.save()
            return Response(
                {
                    "message": "Condition updated successfully.",
                    "condition": SkinConditionSerializer(condition).data,
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        condition.delete()
        return Response(
            {"message": "Condition deleted successfully."},
            status=status.HTTP_200_OK
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def condition_recommendations(request, id):
    condition = get_object_or_404(SkinCondition, id=id)

    recommendation_ids = ConditionRecommendation.objects.filter(
        condition=condition
    ).values_list("recommendation_id", flat=True)

    recommendations = Recommendation.objects.filter(id__in=recommendation_ids)
    serializer = RecommendationSerializer(recommendations, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_recommendation_to_condition(request, id):
    if not is_admin_user(request):
        return admin_required_response()

    condition = get_object_or_404(SkinCondition, id=id)
    recommendation_id = request.data.get("recommendation_id")

    if not recommendation_id:
        return Response(
            {"recommendation_id": "This field is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    recommendation = get_object_or_404(Recommendation, id=recommendation_id)

    relation, created = ConditionRecommendation.objects.get_or_create(
        condition=condition,
        recommendation=recommendation
    )

    return Response(
        {
            "message": "Recommendation added to condition successfully.",
            "created": created,
            "condition": condition.name,
            "recommendation": recommendation.name,
        },
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_recommendation_from_condition(request, id, recommendation_id):
    if not is_admin_user(request):
        return admin_required_response()

    condition = get_object_or_404(SkinCondition, id=id)
    recommendation = get_object_or_404(Recommendation, id=recommendation_id)

    relation = get_object_or_404(
        ConditionRecommendation,
        condition=condition,
        recommendation=recommendation
    )

    relation.delete()

    return Response(
        {"message": "Recommendation removed from condition successfully."},
        status=status.HTTP_200_OK
    )


# RECOMMENDATIONS

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def recommendations_collection(request):
    if request.method == "GET":
        recommendations = Recommendation.objects.all().order_by("name")

        rec_type = request.query_params.get("type")
        search = request.query_params.get("search")

        if rec_type:
            recommendations = recommendations.filter(type=rec_type)

        if search:
            recommendations = recommendations.filter(name__icontains=search)

        serializer = RecommendationSerializer(recommendations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        if not is_admin_user(request):
            return admin_required_response()

        serializer = RecommendationSerializer(data=request.data)

        if serializer.is_valid():
            recommendation = serializer.save()
            return Response(
                {
                    "message": "Recommendation created successfully.",
                    "recommendation": RecommendationSerializer(recommendation).data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def recommendation_detail(request, id):
    recommendation = get_object_or_404(Recommendation, id=id)

    if request.method == "GET":
        serializer = RecommendationSerializer(recommendation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if not is_admin_user(request):
        return admin_required_response()

    if request.method in ("PUT", "PATCH"):
        partial = request.method == "PATCH"
        serializer = RecommendationSerializer(recommendation, data=request.data, partial=partial)

        if serializer.is_valid():
            recommendation = serializer.save()
            return Response(
                {
                    "message": "Recommendation updated successfully.",
                    "recommendation": RecommendationSerializer(recommendation).data,
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        recommendation.delete()
        return Response(
            {"message": "Recommendation deleted successfully."},
            status=status.HTTP_200_OK
        )
