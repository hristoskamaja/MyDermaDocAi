from django.db import models


# ---------------------------------------------------------------------------
# Исти choices како во leafscan (Severity), плус нов ConditionCategory
# наместо PlantType/DiseaseCategory - за кожа нема "тип на растение",
# затоа наместо Plant + Disease тука има само еден модел: SkinCondition.
# ---------------------------------------------------------------------------

class Severity(models.TextChoices):
    LOW = "LOW", "Low"
    MEDIUM = "MEDIUM", "Medium"
    HIGH = "HIGH", "High"


class ConditionCategory(models.TextChoices):
    BENIGN = "BENIGN", "Benign"
    PRECANCEROUS = "PRECANCEROUS", "Precancerous"
    MALIGNANT = "MALIGNANT", "Malignant"
    INFLAMMATORY = "INFLAMMATORY", "Inflammatory"
    OTHER = "OTHER", "Other"


class RecommendationType(models.TextChoices):
    SELF_CARE = "SELF_CARE", "Self-care"
    MEDICAL_CONSULT = "MEDICAL_CONSULT", "Medical consultation"
    LIFESTYLE = "LIFESTYLE", "Lifestyle"


class SkinCondition(models.Model):
    """
    ВАЖНО: полето `key` мора точно да се совпаѓа со имињата во
    `class_names` од skin_model.pt (пр. "melanoma", "basal_cell_carcinoma"...).
    Тоа е она што AI моделот го враќа - views.py потоа го бара records по `key`
    за да ги извади description/severity/препораки.

    Оваа табела ја полниш еднаш со `python manage.py seed_skin_conditions`
    (core/management/commands/seed_skin_conditions.py), а потоа описите/
    симптомите ги дотеруваш рачно преку Django admin или React admin панелот
    (исто како Diseases страницата во leafscan_web).
    """

    key = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    symptoms = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="conditions/", blank=True, null=True)
    image_description = models.TextField(blank=True, null=True)
    severity = models.CharField(
        max_length=10,
        choices=Severity.choices,
        blank=True,
        null=True,
    )
    category = models.CharField(
        max_length=20,
        choices=ConditionCategory.choices,
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "skin_conditions"

    def __str__(self):
        return self.name


class Recommendation(models.Model):
    """
    Го заменува Treatment од leafscan. Намерно НЕ се вика "Treatment" /
    "лек" - апликацијата не смее да дава медицински третман/дозирање,
    туку општи совети за нега и препорака за преглед кај лекар.
    """

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(
        max_length=20,
        choices=RecommendationType.choices,
    )

    class Meta:
        db_table = "recommendations"

    def __str__(self):
        return self.name


class ConditionRecommendation(models.Model):
    condition = models.ForeignKey(
        SkinCondition,
        on_delete=models.CASCADE,
        related_name="condition_recommendations",
    )
    recommendation = models.ForeignKey(
        Recommendation,
        on_delete=models.CASCADE,
        related_name="condition_recommendations",
    )

    class Meta:
        db_table = "condition_recommendations"
        constraints = [
            models.UniqueConstraint(
                fields=["condition", "recommendation"],
                name="unique_condition_recommendation",
            )
        ]

    def __str__(self):
        return f"{self.condition.name} - {self.recommendation.name}"
