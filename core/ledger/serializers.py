from rest_framework import serializers

from .models import Account, Category, Transaction


class AccountSerializer(serializers.ModelSerializer):
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


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "organization", "name", "description", "parent", "created_at"]
        read_only_fields = ["id", "created_at"]


class TransactionSerializer(serializers.ModelSerializer):
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

