from django.db import models


class CompanyQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_active=True)

    def inactive(self):
        return self.filter(is_active=False)

    def deleted(self):
        return self.filter(is_deleted=True)

    def alive(self):
        return self.filter(is_deleted=False)

    def by_slug(self, slug: str):
        return self.filter(slug=slug)

    def by_uuid(self, uuid):
        return self.filter(uuid=uuid)