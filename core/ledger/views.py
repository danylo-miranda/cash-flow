from rest_framework import filters, permissions, viewsets

from organizations.permissions import IsOrganizationMember
from organizations.models import Membership

from .models import Account, Category, Transaction
from .serializers import AccountSerializer, CategorySerializer, TransactionSerializer


class MembershipScopedQuerysetMixin:
    """
    Filtra querysets garantindo que o usuário autenticado participa da organização.
    """

    def filter_by_membership(self, queryset):
        user = self.request.user
        return queryset.filter(organization__memberships__user=user, organization__memberships__is_active=True).distinct()

    def get_organization_filtered_queryset(self, queryset):
        queryset = self.filter_by_membership(queryset)
        organization_id = self.request.query_params.get("organization")
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)
        return queryset


class AccountViewSet(MembershipScopedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [IsOrganizationMember]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "description"]

    def get_queryset(self):
        return self.get_organization_filtered_queryset(Account.objects.all())

    def perform_create(self, serializer):
        organization = serializer.validated_data["organization"]
        Membership.objects.get(user=self.request.user, organization=organization, is_active=True)
        serializer.save()


class CategoryViewSet(MembershipScopedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        return self.get_organization_filtered_queryset(Category.objects.all())


class TransactionViewSet(MembershipScopedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsOrganizationMember]
    filter_backends = [filters.SearchFilter]
    search_fields = ["description", "notes"]

    def get_queryset(self):
        queryset = self.get_organization_filtered_queryset(
            Transaction.objects.select_related("account", "category", "organization", "created_by")
        )

        kind = self.request.query_params.get("kind")
        status = self.request.query_params.get("status")
        if kind:
            queryset = queryset.filter(kind=kind)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
