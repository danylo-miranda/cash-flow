from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from rest_framework import permissions, response, status, viewsets

from organizations.models import Organization
from organizations.permissions import IsOrganizationMember

from .serializers import CashFlowSummaryEntrySerializer
from .services import generate_cashflow_summary


class CashFlowSummaryViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def list(self, request):
        organization_id = request.query_params.get("organization")
        start = request.query_params.get("start")
        end = request.query_params.get("end")

        if not organization_id:
            return response.Response(
                {"detail": "Parâmetro 'organization' é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        organization = get_object_or_404(
            Organization,
            pk=organization_id,
            memberships__user=request.user,
            memberships__is_active=True,
        )

        start_date = parse_date(start) if start else None
        end_date = parse_date(end) if end else None

        if not start_date or not end_date:
            return response.Response(
                {"detail": "Parâmetros 'start' e 'end' devem ser datas válidas (YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = generate_cashflow_summary(organization, start_date, end_date)
        serializer = CashFlowSummaryEntrySerializer(data, many=True)
        return response.Response(serializer.data)
