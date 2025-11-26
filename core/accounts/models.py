from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Administrador"
    FINANCEIRO = "FINANCEIRO", "Financeiro"
    CONSULTOR = "CONSULTOR", "Consultor"
    ANALISTA = "ANALISTA", "Analista"


class User(AbstractUser):
    """
    Usuário base do sistema com papel principal.
    Relações específicas com organizações são feitas via Membership.
    """

    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.ANALISTA,
    )

    def __str__(self) -> str:
        full_name = self.get_full_name()
        return full_name or self.username

# Create your models here.
