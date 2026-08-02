from django.conf import settings
from django.db import models

from core.models import SkinCondition


class Analysis(models.Model):
    analysis_key = models.CharField(max_length=20, unique=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="analyses",
    )

    condition = models.ForeignKey(
        SkinCondition,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="analyses",
    )

    image = models.ImageField(upload_to="analyses/")

    confidence = models.FloatField(blank=True, null=True)

    # AI предвидувањето беше под LOW_CONFIDENCE_THRESHOLD (види
    # skin_model_service.py) - UI треба јасно да прикаже дека резултатот
    # е несигурен и уште повеќе да инсистира на преглед кај лекар.
    is_low_confidence = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analyses"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(confidence__isnull=True)
                | models.Q(confidence__gte=0, confidence__lte=1),
                name="confidence_between_0_and_1",
            )
        ]

    def __str__(self):
        return self.analysis_key
