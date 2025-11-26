from django.conf import settings
from django.db import models


class CashFlowProjection(models.Model):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="cashflow_projections",
    )
    period_start = models.DateField()
    period_end = models.DateField()
    data = models.JSONField(default=dict, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="generated_cashflows",
    )

    class Meta:
        ordering = ["-generated_at"]

    def __str__(self) -> str:
        return f"Cashflow {self.period_start} - {self.period_end}"

# Create your models here.
