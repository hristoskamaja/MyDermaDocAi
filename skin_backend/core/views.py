import threading

from django.db import close_old_connections
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import SkinCondition, Recommendation, ConditionRecommendation, Dermatologist
from .serializers import (
    SkinConditionSerializer,
    RecommendationSerializer,
    LocalizedRecommendationSerializer,
    DermatologistSerializer,
)
from .services.translation import fill_missing_translations

# The three fields that get an auto-generated English counterpart - see
# core/services/translation.py. Kept as one tuple so the "did the source
# text change, so the _en translation needs regenerating" check below and
# fill_missing_translations() can't drift out of sync with each other.
TRANSLATED_FIELD_PAIRS = [
    ("description", "description_en"),
    ("symptoms", "symptoms_en"),
    ("treatment_overview", "treatment_overview_en"),
]


def sync_condition_translations(condition, previous_values=None, protected_fields=None):
    """
    Clears any English field whose Macedonian source just changed (so it
    doesn't keep showing a translation of the *old* text), then fills in
    whatever's missing via Gemini, and saves if anything changed.

    `previous_values` is a dict of {field: old_value}, or None for a
    brand-new condition (nothing to compare against).

    `protected_fields` is the set of _en field names the admin explicitly
    typed a value for IN THIS SAME REQUEST (see condition_detail) - those
    are never auto-cleared/auto-translated, so a manual English edit is
    never silently overwritten by Gemini's version.
    """
    changed = False
    protected_fields = protected_fields or set()

    if previous_values is not None:
        for source_field, target_field in TRANSLATED_FIELD_PAIRS:
            if target_field in protected_fields:
                continue
            new_value = getattr(condition, source_field, None)
            if previous_values.get(source_field) != new_value:
                setattr(condition, target_field, None)
                changed = True

    if fill_missing_translations(condition, skip_fields=protected_fields):
        changed = True

    if changed:
        condition.save()


def sync_condition_translations_in_background(condition_id, previous_values=None, protected_fields=None):
    """
    Same as sync_condition_translations, but fired on a background thread
    so the admin's create/save request returns immediately instead of
    blocking on up to 3 sequential Gemini calls (one per translated field,
    each up to ~15-20s) - that wait made every save feel like it "wasn't
    working". The translated fields simply appear a few seconds later, the
    next time the condition is fetched (e.g. on the next page load/save).

    Re-fetches the condition by id inside the thread rather than reusing
    the instance from the request - Django model instances aren't safe to
    share across threads, and the DB connection used by the request thread
    is closed once the response is sent.
    """

    def worker():
        try:
            condition = SkinCondition.objects.get(id=condition_id)
            sync_condition_translations(condition, previous_values, protected_fields)
        except SkinCondition.DoesNotExist:
            pass
        except Exception as error:
            print(f"Background translation sync failed: {error}")
        finally:
            close_old_connections()

    threading.Thread(target=worker, daemon=True).start()


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
# Equivalent to the Diseases page in leafscan_web/src/pages/Diseases -
# the React admin panel here lists/edits conditions instead of plant diseases.

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
            manual_en_fields = {
                target_field
                for _, target_field in TRANSLATED_FIELD_PAIRS
                if str(request.data.get(target_field, "")).strip()
            }
            sync_condition_translations_in_background(condition.id, protected_fields=manual_en_fields)
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
        previous_values = {
            source_field: getattr(condition, source_field, None)
            for source_field, _ in TRANSLATED_FIELD_PAIRS
        }
        # Any _en field the admin actually typed something into in THIS
        # request is a manual edit - never auto-overwritten by Gemini,
        # even if the Macedonian source also changed in the same save.
        manual_en_fields = {
            target_field
            for _, target_field in TRANSLATED_FIELD_PAIRS
            if str(request.data.get(target_field, "")).strip()
        }
        serializer = SkinConditionSerializer(condition, data=request.data, partial=partial)

        if serializer.is_valid():
            condition = serializer.save()
            sync_condition_translations_in_background(condition.id, previous_values, manual_en_fields)
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
    serializer = LocalizedRecommendationSerializer(
        recommendations, many=True, context={"request": request}
    )

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


# DERMATOLOGISTS
# Manually maintained list (not loaded automatically) - any logged-in user
# (mobile/patient-web) may read it, but only an admin may add/edit/delete
# records. Regular users only see is_active=True records; the admin sees
# everything (including inactive ones) so they can edit them.

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def dermatologists_collection(request):
    if request.method == "GET":
        if is_admin_user(request):
            dermatologists = Dermatologist.objects.all()
        else:
            dermatologists = Dermatologist.objects.filter(is_active=True)

        search = request.query_params.get("search")
        city = request.query_params.get("city")

        if search:
            dermatologists = dermatologists.filter(name__icontains=search)

        if city:
            dermatologists = dermatologists.filter(city__icontains=city)

        serializer = DermatologistSerializer(dermatologists, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        if not is_admin_user(request):
            return admin_required_response()

        serializer = DermatologistSerializer(data=request.data)

        if serializer.is_valid():
            dermatologist = serializer.save()
            return Response(
                {
                    "message": "Dermatologist created successfully.",
                    "dermatologist": DermatologistSerializer(dermatologist).data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def dermatologist_detail(request, id):
    dermatologist = get_object_or_404(Dermatologist, id=id)

    if request.method == "GET":
        if not dermatologist.is_active and not is_admin_user(request):
            return admin_required_response()

        serializer = DermatologistSerializer(dermatologist)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if not is_admin_user(request):
        return admin_required_response()

    if request.method in ("PUT", "PATCH"):
        partial = request.method == "PATCH"
        serializer = DermatologistSerializer(dermatologist, data=request.data, partial=partial)

        if serializer.is_valid():
            dermatologist = serializer.save()
            return Response(
                {
                    "message": "Dermatologist updated successfully.",
                    "dermatologist": DermatologistSerializer(dermatologist).data,
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        dermatologist.delete()
        return Response(
            {"message": "Dermatologist deleted successfully."},
            status=status.HTTP_200_OK
        )
