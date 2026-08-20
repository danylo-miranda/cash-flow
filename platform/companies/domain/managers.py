import uuid

from django.db import models

from .querysets import CompanyQuerySet


class CompanyManager(models.Manager):

    def get_queryset(self):

        return CompanyQuerySet(
            self.model,
            using=self._db
        )

    def active(self):

        return self.get_queryset().active()

    def create_company(

        self,

        name: str,

        slug: str,

        owner_email: str,

    ):

        return self.create(

            uuid=uuid.uuid4(),

            name=name,

            slug=slug,

            owner_email=owner_email,

        )