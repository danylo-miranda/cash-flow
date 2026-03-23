from rest_framework import mixins, permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from .models import Membership, Organization
from .permissions import IsOrganizationMember
from .serializers import MembershipSerializer, OrganizationSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Organization.objects.filter(memberships__user=user, memberships__is_active=True).distinct()

    def perform_create(self, serializer):
        organization = serializer.save()
        Membership.objects.create(
            user=self.request.user,
            organization=organization,
            role="OWNER",
            is_active=True,
        )


class MembershipViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = MembershipSerializer
    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        organization_id = self.request.query_params.get("organization")
        qs = Membership.objects.filter(
            organization__memberships__user=self.request.user,
            organization__memberships__is_active=True,
            is_active=True,
        ).distinct()
        if organization_id:
            qs = qs.filter(organization_id=organization_id)
        return qs.select_related("user", "organization")

    def perform_update(self, serializer):
        membership = serializer.instance
        requester_membership = Membership.objects.filter(
            user=self.request.user,
            organization=membership.organization,
            is_active=True,
        ).first()
        if not requester_membership or requester_membership.role not in {"OWNER", "ADMIN"}:
            raise PermissionDenied("Você não possui permissão para alterar membros.")
        serializer.save()
