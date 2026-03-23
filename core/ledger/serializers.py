from rest_framework import serializers

from organizations.models import Membership

from .models import Account, Category, Transaction


class OrganizationBoundSerializerMixin:
    organization_field_name = "organization"

    def get_target_organization(self, attrs):
        organization = attrs.get(self.organization_field_name)
        if organization is not None:
            return organization
        if self.instance is not None:
            return getattr(self.instance, self.organization_field_name, None)
        return None

    def validate_organization_membership(self, organization):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return
        if not Membership.objects.filter(
            user=request.user,
            organization=organization,
            is_active=True,
        ).exists():
            raise serializers.ValidationError(
                {"organization": "Voce nao possui acesso ativo a esta organizacao."}
            )

    def validate_parent_organization(self, attrs):
        organization = self.get_target_organization(attrs)
        parent = attrs.get("parent")
        if parent is not None and organization is not None and parent.organization_id != organization.id:
            raise serializers.ValidationError(
                {"parent": "O parent precisa pertencer a mesma organizacao."}
            )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        organization = self.get_target_organization(attrs)
        if organization is not None:
            self.validate_organization_membership(organization)
        return attrs


class AccountSerializer(OrganizationBoundSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            "id",
            "organization",
            "name",
            "description",
            "type",
            "parent",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        self.validate_parent_organization(attrs)
        return attrs


class CategorySerializer(OrganizationBoundSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "organization", "name", "description", "parent", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        self.validate_parent_organization(attrs)
        return attrs


class TransactionSerializer(OrganizationBoundSerializerMixin, serializers.ModelSerializer):
    account_detail = AccountSerializer(source="account", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "organization",
            "account",
            "account_detail",
            "category",
            "kind",
            "status",
            "amount",
            "competence_date",
            "payment_date",
            "description",
            "notes",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at", "account_detail"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        organization = self.get_target_organization(attrs)
        account = attrs.get("account") or getattr(self.instance, "account", None)
        category = attrs.get("category", getattr(self.instance, "category", None))

        if account is not None and organization is not None and account.organization_id != organization.id:
            raise serializers.ValidationError(
                {"account": "A conta precisa pertencer a mesma organizacao da transacao."}
            )

        if category is not None and organization is not None and category.organization_id != organization.id:
            raise serializers.ValidationError(
                {"category": "A categoria precisa pertencer a mesma organizacao da transacao."}
            )

        return attrs

