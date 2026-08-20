from rest_framework import permissions

from .models import Membership, Organization


class IsOrganizationMember(permissions.BasePermission):
    """
    Garante que o usuário autenticado participa da organização alvo.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        organization = obj if isinstance(obj, Organization) else getattr(obj, "organization", None)
        if organization is None:
            return False
        return Membership.objects.filter(
            user=request.user,
            organization=organization,
            is_active=True,
        ).exists()

