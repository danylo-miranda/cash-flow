from rest_framework import serializers

from .models import Membership, Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "slug", "currency", "timezone", "created_at", "updated_at"]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]


class MembershipSerializer(serializers.ModelSerializer):
    user_display = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = Membership
        fields = [
            "id",
            "user",
            "user_display",
            "organization",
            "role",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "user_display", "created_at", "user", "organization"]

