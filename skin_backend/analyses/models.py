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

    # The AI prediction was below LOW_CONFIDENCE_THRESHOLD (see
    # skin_model_service.py) - the UI must clearly show that the result
    # is uncertain and push even harder for a doctor visit.
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


class ChatRole(models.TextChoices):
    USER = "USER", "User"
    ASSISTANT = "ASSISTANT", "Assistant"


class AnalysisChatMessage(models.Model):
    """
    Q&A history tied to a specific analysis - lets the user ask follow-up
    questions about the detected condition. Gemini answers under the same
    constraints as gemini_service.py (no diagnosis/prescribing), and the
    answer is NOT cached because each question is personal and different
    per user (unlike Recommendation, which is the same for everyone).
    """

    analysis = models.ForeignKey(
        Analysis,
        on_delete=models.CASCADE,
        related_name="chat_messages",
    )
    role = models.CharField(max_length=10, choices=ChatRole.choices)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analysis_chat_messages"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.analysis.analysis_key} [{self.role}]"
