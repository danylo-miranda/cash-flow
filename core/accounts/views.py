from rest_framework import mixins, permissions, viewsets

from organizations.models import Membership

from .models import User
from .serializers import UserSerializer


class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Endpoints de leitura de usuários. Operações administrativas ficam no Django Admin.
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        organization_ids = Membership.objects.filter(
            user=self.request.user,
            is_active=True,
        ).values_list("organization_id", flat=True)
        return User.objects.filter(
            is_active=True,
            memberships__organization_id__in=organization_ids,
            memberships__is_active=True,
        ).distinct()
