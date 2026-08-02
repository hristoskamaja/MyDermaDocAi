from django.urls import path

from . import views

urlpatterns = [
    # Dashboard
    path("dashboard/overview/", views.dashboard_overview, name="dashboard_overview"),
    path("dashboard/summary/", views.dashboard_summary, name="dashboard_summary"),
    path("dashboard/monthly-trend/", views.dashboard_monthly_trend, name="dashboard_monthly_trend"),
    path("dashboard/condition-distribution/", views.dashboard_condition_distribution, name="dashboard_condition_distribution"),
    path("dashboard/recent-analyses/", views.dashboard_recent_analyses, name="dashboard_recent_analyses"),
    path("dashboard/top-detected-conditions/", views.dashboard_top_detected_conditions, name="dashboard_top_detected_conditions"),

    # Statistics
    path("statistics/overview/", views.statistics_overview, name="statistics_overview"),
    path("statistics/analyses-by-month/", views.statistics_analyses_by_month, name="statistics_analyses_by_month"),
    path("statistics/conditions-by-category/", views.statistics_conditions_by_category, name="statistics_conditions_by_category"),
    path("statistics/user-growth/", views.statistics_user_growth, name="statistics_user_growth"),
    path("statistics/detection-accuracy/", views.statistics_detection_accuracy, name="statistics_detection_accuracy"),
    path("statistics/top-detected-conditions/", views.statistics_top_detected_conditions, name="statistics_top_detected_conditions"),
]
