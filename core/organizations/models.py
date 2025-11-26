from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify


class Organization(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    currency = models.CharField(max_length=5, default="BRL")
    timezone = models.CharField(max_length=64, default="America/Sao_Paulo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class MembershipRole(models.TextChoices):
    OWNER = "OWNER", "Proprietário"
    ADMIN = "ADMIN", "Administrador"
    FINANCEIRO = "FINANCEIRO", "Financeiro"
    CONSULTOR = "CONSULTOR", "Consultor"
    ANALISTA = "ANALISTA", "Analista"


class Membership(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=MembershipRole.choices,
        default=MembershipRole.ANALISTA,
    )
    is_active = models.BooleanField(default=True)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="invited_memberships",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "organization")
        verbose_name = "membership"
        verbose_name_plural = "memberships"

    def __str__(self) -> str:
        return f"{self.user} @ {self.organization}"

# Create your models here.
