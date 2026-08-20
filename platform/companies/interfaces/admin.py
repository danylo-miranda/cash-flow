from django.contrib import admin

from .models import Company


@admin.register(Company)

class CompanyAdmin(admin.ModelAdmin):

    list_display = (

        "name",

        "slug",

        "owner_email",

        "is_active",

        "created_at",

    )

    search_fields = (

        "name",

        "slug",

        "owner_email",

    )

    list_filter = (

        "is_active",

    )

    ordering = ("name",)