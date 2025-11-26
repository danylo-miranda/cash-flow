from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ledger.models import Account, AccountType, Transaction, TransactionType
from organizations.models import Membership, Organization


class CashFlowSummaryTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="cashflow", password="pass123")
        self.organization = Organization.objects.create(name="Cash Org")
        Membership.objects.create(user=self.user, organization=self.organization)
        self.account = Account.objects.create(
            organization=self.organization,
            name="Conta Geral",
            type=AccountType.RECEITA,
        )

    def test_cashflow_summary_returns_series(self):
        self.client.force_authenticate(self.user)
        today = date.today()
        Transaction.objects.create(
            organization=self.organization,
            account=self.account,
            kind=TransactionType.RECEITA,
            amount="1000.00",
            competence_date=today,
        )
        Transaction.objects.create(
            organization=self.organization,
            account=self.account,
            kind=TransactionType.DESPESA,
            amount="400.00",
            competence_date=today + timedelta(days=1),
        )

        url = reverse("cashflow-list")
        response = self.client.get(
            url,
            data={
                "organization": self.organization.id,
                "start": today.isoformat(),
                "end": (today + timedelta(days=2)).isoformat(),
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]["inflow"], "1000.00")
