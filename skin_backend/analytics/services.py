"""
Adapted from leafscan/analytics/services.py.

Differences from the original:
- Analysis.condition instead of Analysis.plant/Analysis.disease
- No HEALTHY/INFECTED result (every analysis always recognizes some
  condition from the lesion datasets) - instead of "healthy count" we
  track low_confidence_rate (how many analyses had an uncertain prediction)
- "diseases_by_category" -> "conditions_by_category", uses
  SkinCondition.category (BENIGN/PRECANCEROUS/MALIGNANT/INFLAMMATORY/OTHER)
"""

from calendar import month_abbr
from datetime import date

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from django.db.models.functions import TruncMonth

from analyses.models import Analysis


def normalize_confidence(value):
    """
    Supports both formats:
    - 0.947 -> 94.7
    - 94.7  -> 94.7
    """
    if value is None:
        return 0

    value = float(value)

    if value <= 1:
        value = value * 100

    return round(value, 1)


def month_label(month_date):
    if not month_date:
        return ""

    return month_abbr[month_date.month]


def add_months(source_date, months):
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    return date(year, month, 1)


def get_last_months(count=8):
    today = date.today()
    current_month = date(today.year, today.month, 1)

    months = []
    start_month = add_months(current_month, -(count - 1))

    for i in range(count):
        months.append(add_months(start_month, i))

    return months


def get_user_date_field():
    User = get_user_model()
    field_names = [field.name for field in User._meta.fields]

    if "created_at" in field_names:
        return "created_at"

    return "date_joined"


def get_analysis_monthly_counts(months_count=8):
    months = get_last_months(months_count)
    start_date = months[0]

    queryset = (
        Analysis.objects
        .filter(created_at__date__gte=start_date)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    data_map = {
        item["month"].date().replace(day=1): item["count"]
        for item in queryset
        if item["month"]
    }

    return [
        {
            "month": month_label(month),
            "count": data_map.get(month, 0)
        }
        for month in months
    ]


def get_user_growth(months_count=8):
    User = get_user_model()
    user_date_field = get_user_date_field()

    months = get_last_months(months_count)
    start_date = months[0]

    filter_kwargs = {
        f"{user_date_field}__date__gte": start_date
    }

    queryset = (
        User.objects
        .filter(**filter_kwargs)
        .annotate(month=TruncMonth(user_date_field))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    data_map = {
        item["month"].date().replace(day=1): item["count"]
        for item in queryset
        if item["month"]
    }

    return [
        {
            "month": month_label(month),
            "count": data_map.get(month, 0)
        }
        for month in months
    ]


def get_detection_accuracy(months_count=8):
    months = get_last_months(months_count)
    start_date = months[0]

    queryset = (
        Analysis.objects
        .filter(created_at__date__gte=start_date)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(accuracy=Avg("confidence"))
        .order_by("month")
    )

    data_map = {
        item["month"].date().replace(day=1): normalize_confidence(item["accuracy"])
        for item in queryset
        if item["month"]
    }

    return [
        {
            "month": month_label(month),
            "accuracy": data_map.get(month, 0)
        }
        for month in months
    ]


def get_dashboard_summary():
    User = get_user_model()

    total_analyses = Analysis.objects.count()
    total_users = User.objects.count()

    conditions_detected = (
        Analysis.objects
        .exclude(condition__isnull=True)
        .values("condition")
        .distinct()
        .count()
    )

    avg_confidence = Analysis.objects.aggregate(avg=Avg("confidence"))["avg"]
    accuracy_rate = normalize_confidence(avg_confidence)

    low_confidence_count = Analysis.objects.filter(is_low_confidence=True).count()
    low_confidence_rate = (
        round((low_confidence_count / total_analyses) * 100, 1)
        if total_analyses else 0
    )

    return {
        "total_analyses": total_analyses,
        "total_users": total_users,
        "conditions_detected": conditions_detected,
        "accuracy_rate": accuracy_rate,
        "low_confidence_rate": low_confidence_rate,
        "growth": {
            "analyses": 0,
            "users": 0,
            "conditions": 0,
            "accuracy": 0
        }
    }


def get_dashboard_condition_distribution():
    data = (
        Analysis.objects
        .exclude(condition__isnull=True)
        .values("condition__name")
        .annotate(value=Count("id"))
        .order_by("-value")
    )

    return [
        {
            "name": item["condition__name"],
            "value": item["value"]
        }
        for item in data
    ]


def get_dashboard_recent_analyses(limit=5):
    analyses = (
        Analysis.objects
        .select_related("condition", "user")
        .order_by("-created_at")[:limit]
    )

    return [
        {
            "id": analysis.id,
            "analysis_key": analysis.analysis_key,
            "condition": analysis.condition.name if analysis.condition else None,
            "severity": analysis.condition.severity if analysis.condition else None,
            "confidence": normalize_confidence(analysis.confidence),
            "is_low_confidence": analysis.is_low_confidence,
            "created_at": analysis.created_at
        }
        for analysis in analyses
    ]


def get_top_detected_conditions(limit=6):
    queryset = (
        Analysis.objects
        .exclude(condition__isnull=True)
        .values("condition__name")
        .annotate(count=Count("id"))
        .order_by("-count")[:limit]
    )

    return [
        {
            "name": item["condition__name"],
            "count": item["count"]
        }
        for item in queryset
    ]


def get_conditions_by_category():
    total_analyses = Analysis.objects.count()

    if total_analyses == 0:
        return []

    data = (
        Analysis.objects
        .exclude(condition__isnull=True)
        .values("condition__category")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    result = []

    for item in data:
        category = item["condition__category"] or "UNKNOWN"
        count = item["count"]

        result.append({
            "category": category,
            "count": count,
            "percentage": round((count / total_analyses) * 100, 1)
        })

    return result


def get_dashboard_overview():
    return {
        "summary": get_dashboard_summary(),
        "monthly_trend": get_analysis_monthly_counts(),
        "condition_distribution": get_dashboard_condition_distribution(),
        "recent_analyses": get_dashboard_recent_analyses(),
        "top_detected_conditions": get_top_detected_conditions()
    }


def get_statistics_overview():
    return {
        "analyses_by_month": get_analysis_monthly_counts(),
        "conditions_by_category": get_conditions_by_category(),
        "user_growth": get_user_growth(),
        "detection_accuracy": get_detection_accuracy(),
        "top_detected_conditions": get_top_detected_conditions()
    }
