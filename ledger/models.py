from decimal import Decimal

from django.conf import settings
from django.db import models


class AccountType(models.TextChoices):
    RECEITA = "RECEITA", "Receita"
    DESPESA = "DESPESA", "Despesa"
    CUSTO = "CUSTO", "Custo"
    INVESTIMENTO = "INVESTIMENTO", "Investimento"
    IMPOSTO = "IMPOSTO", "Imposto"


class Account(models.Model):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="accounts",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=AccountType.choices)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("organization", "name", "type")
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.organization})"


class Category(models.Model):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="categories",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("organization", "name")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class TransactionType(models.TextChoices):
    RECEITA = "RECEITA", "Receita"
    DESPESA = "DESPESA", "Despesa"
    INVESTIMENTO = "INVESTIMENTO", "Investimento"
    IMPOSTO = "IMPOSTO", "Imposto"
    CUSTO = "CUSTO", "Custo"


class TransactionStatus(models.TextChoices):
    PLANNED = "PLANNED", "Prevista"
    CONFIRMED = "CONFIRMED", "Confirmada"


class Transaction(models.Model):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="transactions",
    )
    kind = models.CharField(max_length=20, choices=TransactionType.choices)
    status = models.CharField(max_length=20, choices=TransactionStatus.choices, default=TransactionStatus.PLANNED)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    competence_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_transactions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-competence_date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.kind} - {self.amount}"

# Create your models here.
