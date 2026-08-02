from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .services import (
    get_analysis_monthly_counts,
    get_conditions_by_category,
    get_dashboard_condition_distribution,
    get_dashboard_overview,
    get_dashboard_recent_analyses,
    get_dashboard_summary,
    get_detection_accuracy,
    get_statistics_overview,
    get_top_detected_conditions,
    get_user_growth,
)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def dashboard_overview(request):
    return Response(get_dashboard_overview(), status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def dashboard_summary(request):
    return Response(get_dashboard_summary(), status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def dashboard_monthly_trend(request):
    return Response(get_analysis_monthly_counts(), status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def dashboard_condition_distribution(request):
    return Response(get_dashboard_condition_distribution(), status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def dashboard_recent_analyses(request):
    return Response(get_dashboard_recent_analyses(), status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def dashboard_top_detected_conditions(request):
    return Response(get_top_detected_conditions(), status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def statistics_overview(request):
    return Response(get_statistics_overview(), status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def statistics_analyses_by_month(request):
    return Response(get_analysis_monthly_counts(), status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def statistics_conditions_by_category(request):
    return Response(get_conditions_by_category(), status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def statistics_user_growth(request):
    return Response(get_user_growth(), status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def statistics_detection_accuracy(request):
    return Response(get_detection_accuracy(), status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def statistics_top_detected_conditions(request):
    return Response(get_top_detected_conditions(), status=status.HTTP_200_OK)
