from .models import Company


class CompanyService:

    @staticmethod
    def create(**kwargs):

        return Company.objects.create_company(**kwargs)

    @staticmethod
    def activate(company):

        company.is_active = True

        company.save(update_fields=["is_active"])

    @staticmethod
    def deactivate(company):

        company.is_active = False

        company.save(update_fields=["is_active"])