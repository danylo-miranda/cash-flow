import uuid

from django.db import models

from django.utils import timezone

from .managers import CompanyManager

from .validators import validate_slug


class Company(models.Model):

    uuid = models.UUIDField(

        default=uuid.uuid4,

        editable=False,

        unique=True,

    )

    name = models.CharField(

        max_length=150,

    )

    slug = models.SlugField(

        max_length=120,

        unique=True,

        validators=[validate_slug],

    )

    owner_email = models.EmailField()

    phone = models.CharField(

        max_length=20,

        blank=True,

    )

    document = models.CharField(

        max_length=20,

        blank=True,

    )

    logo = models.ImageField(

        upload_to="companies/logos/",

        blank=True,

        null=True,

    )

    timezone = models.CharField(

        max_length=50,

        default="America/Sao_Paulo",

    )

    language = models.CharField(

        max_length=10,

        default="pt-BR",

    )

    currency = models.CharField(

        max_length=5,

        default="BRL",

    )

    is_active = models.BooleanField(

        default=True,

    )

    is_deleted = models.BooleanField(

        default=False,

    )

    created_at = models.DateTimeField(

        auto_now_add=True,

    )

    updated_at = models.DateTimeField(

        auto_now=True,

    )

    deleted_at = models.DateTimeField(

        blank=True,

        null=True,

    )

    objects = CompanyManager()

    class Meta:

        ordering = ["name"]

        indexes = [

            models.Index(fields=["slug"]),

            models.Index(fields=["uuid"]),

            models.Index(fields=["is_active"]),

        ]

        verbose_name = "Company"

        verbose_name_plural = "Companies"

    def soft_delete(self):

        self.is_deleted = True

        self.deleted_at = timezone.now()

        self.save(update_fields=[

            "is_deleted",

            "deleted_at",

        ])

    def restore(self):

        self.is_deleted = False

        self.deleted_at = None

        self.save(update_fields=[

            "is_deleted",

            "deleted_at",

        ])

    def __str__(self):

        return self.name