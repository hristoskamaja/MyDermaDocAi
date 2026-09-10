from django.db import models


# ---------------------------------------------------------------------------
# Same choices as in leafscan (Severity), plus a new ConditionCategory
# instead of PlantType/DiseaseCategory - skin has no "plant type", so
# instead of Plant + Disease there's just one model here: SkinCondition.
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
    IMPORTANT: the `key` field must exactly match the names in
    `class_names` from skin_model.pt (e.g. "melanoma", "basal_cell_carcinoma"...).
    That's what the AI model returns - views.py then looks up records by
    `key` to pull out the description/severity/recommendations.

    Fill this table once with `python manage.py seed_skin_conditions`
    (core/management/commands/seed_skin_conditions.py), then adjust the
    descriptions/symptoms by hand through the Django admin or React admin
    panel (same as the Diseases page in leafscan_web).
    """

    key = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    symptoms = models.TextField(blank=True, null=True)

    # DELIBERATELY "treatment_overview", not "treatment" / "prescription":
    # this is a general, educational description of what dermatologists
    # TYPICALLY use for this condition (same spirit as gemini_service.py -
    # never a specific medication/dose/personal advice). Always shown
    # together with a reminder that a doctor, not the app, makes the final
    # treatment decision.
    treatment_overview = models.TextField(blank=True, null=True)

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


class Dermatologist(models.Model):
    """
    Manually maintained list of dermatologists - NOT loaded/scraped
    automatically from external sources (that's a deliberate decision:
    scraping real doctor/appointment data is fragile and a legal/ToS risk).
    The admin (a non-technical user) manually enters the real dermatologists
    she knows about through the React admin panel, same as SkinCondition
    above. The table can legitimately be empty until the admin adds
    records - that's not a bug, the UI must clearly show that instead of
    displaying fabricated/fake contact info.
    """

    name = models.CharField(max_length=150)
    clinic_name = models.CharField(max_length=150, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "dermatologists"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Recommendation(models.Model):
    """
    Replaces Treatment from leafscan. Deliberately NOT called "Treatment" /
    "medication" - the app must not give medical treatment/dosing, only
    general care advice and a recommendation to see a doctor.
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
